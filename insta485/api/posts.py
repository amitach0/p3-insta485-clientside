"""REST API for posts."""
import flask
import hashlib
import insta485
# import InvalidUsage from errors


# HELPER FUNCTIONS
def authentication():
    """Authenticate user."""
    if 'username' in flask.session:
        logname = flask.session['username']
    else:
        if flask.request.authorization:
            logname = flask.request.authorization['username']
            password = flask.request.authorization['password']
        else:
            return flask.abort(403)

        algorithm = 'sha512'
        salt = 'a45ffdcc71884853a2cba9e6bc55e812'
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        connection = insta485.model.get_db()
        cur = connection.execute(
          "SELECT username, password "
          "FROM users "
          "WHERE username = ? AND password = ? ",
          (logname, password_db_string)
        )
        is_valid = len(cur.fetchall())
        if is_valid == 1:
            return logname
        else:
            return flask.abort(403)
    return logname


@insta485.app.route('/api/v1/')
def get_api():
    """Return list of services available."""
    context = {
      "comments": "/api/v1/comments/",
      "likes": "/api/v1/likes/",
      "posts": "/api/v1/posts/",
      "url": "/api/v1/"
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_posts():
    """Return the 10 newest posts."""
    logname = authentication()
    connection = insta485.model.get_db()

    # Pagination
    size = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)
    postid_lte = flask.request.args.get('postid_lte')

    # Check errors
    if size < 0 or page < 0:
        flask.abort(400)

    # postid_lte passed
    if postid_lte is not None:
        cur = connection.execute(
          "SELECT postid "
          "FROM ("
          "SELECT P.postid, U.username AS owner, U.filename AS "
          "owner_img_url, P.filename as img_url, P.created AS "
          "timestamp "
          "FROM users U "
          "INNER JOIN posts P ON U.username = P.owner "
          "WHERE U.username = ? "
          "GROUP BY P.postid, U.username, U.filename, P.filename, P.created "
          "UNION "
          "SELECT P.postid, F.username2 AS owner, U2.filename as "
          "owner_img_url, P.filename as img_url, "
          "P.created AS timestamp "
          "FROM users U "
          "INNER JOIN following F ON U.username = F.username1 "
          "INNER JOIN users U2 ON F.username2 = U2.username "
          "INNER JOIN posts P ON F.username2 = P.owner "
          "WHERE U.username = ? "
          "GROUP BY P.postid, F.username2, "
          "U2.filename, P.filename, P.created) "
          "WHERE postid <= ?"
          "ORDER BY timestamp, postid DESC LIMIT ? OFFSET ? ",
          (logname, logname, postid_lte, size, (page * size))
        )
    else:
        cur = connection.execute(
          "SELECT postid "
          "FROM ("
          "SELECT P.postid, U.username AS owner, U.filename AS "
          "owner_img_url, P.filename as img_url, P.created AS "
          "timestamp "
          "FROM users U "
          "INNER JOIN posts P ON U.username = P.owner "
          "WHERE U.username = ? "
          "GROUP BY P.postid, U.username, U.filename, P.filename, P.created "
          "UNION "
          "SELECT P.postid, F.username2 AS owner, U2.filename as "
          "owner_img_url, P.filename as img_url, "
          "P.created AS timestamp "
          "FROM users U "
          "INNER JOIN following F ON U.username = F.username1 "
          "INNER JOIN users U2 ON F.username2 = U2.username "
          "INNER JOIN posts P ON F.username2 = P.owner "
          "WHERE U.username = ? "
          "GROUP BY P.postid, F.username2, "
          "U2.filename, P.filename, P.created) "
          "ORDER BY timestamp, postid DESC LIMIT ? OFFSET ?",
          (logname, logname, size, (page * size))
        )

    postids = cur.fetchall()

    if postid_lte is None:
        postid_lte = max(postids, key=lambda x: x['postid'])['postid']

    if len(postids) < size:
        context = {"next": "", "results": []}
    else:
        context = {"next":
                   "/api/v1/posts/?size={}&page={}&postid_lte={}".format(
                     size, page+1, postid_lte), "results": []}

    for post in postids:
        curr_post = {'postid': post['postid'], 'url':
                     '/api/v1/posts/{}/'.format(int(post['postid']))}
        context['results'].append(curr_post)

    if '8000' in flask.request.url:
        context['url'] = flask.request.url.split("8000", 1)[1]
    else:
        context['url'] = flask.request.url.split("host", 1)[1]

    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    logname = authentication()
    connection = insta485.model.get_db()

    cur = connection.execute(
      "SELECT commentid, owner, text "
      "FROM comments "
      "WHERE postid = ? "
      " ORDER BY commentid ",
      (postid_url_slug,)
    )

    comments = cur.fetchall()

    for comment in comments:
        if comment['owner'] == logname:
            comment['lognameOwnsThis'] = True
        else:
            comment['lognameOwnsThis'] = False

        comment['ownerShowUrl'] = '/users/{}/'.format(comment['owner'])
        comment['url'] = '/api/v1/comments/{}/'.format(comment['commentid'])

    context = {'comments': comments}
    comments_url = '/api/v1/comments/?postid={}'.format(postid_url_slug)
    context['comments_url'] = comments_url

    # Post and owner details
    cur = connection.execute(
      "SELECT P.created, P.filename as imgUrl, P.owner, "
      "U.filename as ownerImgUrl "
      "FROM posts P "
      "INNER JOIN users U ON P.owner = U.username "
      "WHERE P.postid = ? ",
      (postid_url_slug,)
    )

    post_dets = cur.fetchall()

    # Error check
    if len(post_dets) == 0:
        flask.abort(404)

    context['created'] = post_dets[0]['created']
    context['imgUrl'] = '/uploads/{}'.format(post_dets[0]['imgUrl'])
    # Likes details - check if logname liked post
    cur = connection.execute(
      "SELECT likeid "
      "FROM likes "
      "WHERE postid = ? AND owner = ? ",
      (postid_url_slug, logname)
    )
    likeid = cur.fetchall()

    # Get total number of likes
    cur = connection.execute(
      "SELECT COUNT(*) "
      "FROM likes "
      "WHERE postid = ? ",
      (postid_url_slug,)
    )
    num_likes = cur.fetchall()
    if len(likeid) != 0:
        context['likes'] = {'lognameLikesThis':
                            True,
                            "numLikes":
                            num_likes[0]['COUNT(*)'],
                            'url':
                            '/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
    else:
        context['likes'] = {'lognameLikesThis':
                            False,
                            "numLikes":
                            num_likes[0]['COUNT(*)'],
                            'url':
                            None}

    # Post and owner details cont.
    context['owner'] = post_dets[0]['owner']
    context['ownerImgUrl'] = '/uploads/{}'.format(post_dets[0]['ownerImgUrl'])
    context['ownerShowUrl'] = '/users/{}/'.format(post_dets[0]['owner'])
    context['postShowUrl'] = '/posts/{}/'.format(postid_url_slug)
    context['postid'] = postid_url_slug
    context['url'] = '/api/v1/posts/{}/'.format(postid_url_slug)

    return flask.jsonify(**context)


@insta485.app.route("/api/v1/likes/", methods=['POST'])
def post_likes():
    """Post likeid."""
    # ?postid=<postid>
    logname = authentication()
    connection = insta485.model.get_db()

    postid = flask.request.args.get('postid')

    cur = connection.execute(
      "SELECT likeid "
      "FROM likes "
      "WHERE postid = ? AND owner = ? ",
      (postid, logname)
    )
    likeid = cur.fetchall()
    print(likeid)
    if len(likeid) == 0:
        connection.execute(
          "INSERT INTO likes (owner, postid, created) "
          "VALUES (?, ?, CURRENT_TIMESTAMP) ",
          (logname, postid)
        )

        cur = connection.execute(
          "SELECT likeid "
          "FROM likes "
          "WHERE postid = ? AND owner = ? ",
          (postid, logname)
        )
        likeid = cur.fetchall()
        context = {'likeid':
                   likeid[0]['likeid'],
                   'url':
                   '/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
        return flask.jsonify(**context), 201
    else:
        context = {'likeid':
                   likeid[0]['likeid'],
                   'url':
                   '/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
        return flask.jsonify(**context)


@insta485.app.route('/api/v1/likes/<int:likeid>/',  methods=['DELETE'])
def delete_like(likeid):
    """Delete like."""
    logname = authentication()
    connection = insta485.model.get_db()

    cur = connection.execute(
      "SELECT likeid, owner "
      "FROM likes "
      "WHERE likeid = ?",
      (likeid,)
    )

    like = cur.fetchall()

    if len(like) == 0:
        flask.abort(404)

    if like[0]['owner'] != logname:
        flask.abort(403)

    connection.execute(
      "DELETE FROM likes WHERE likeid = ?",
      (likeid,)
    )

    return flask.jsonify({}), 204


@insta485.app.route('/api/v1/comments/',  methods=['POST'])
def post_comment():
    """Post comment."""
    postid = flask.request.args.get('postid')
    logname = authentication()
    connection = insta485.model.get_db()

    text = flask.request.json.get("text", None)

    connection.execute(
      "INSERT INTO comments (owner, postid, text, created) "
      "VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
      (logname, postid, text)
    )

    cur = connection.execute("SELECT last_insert_rowid()")
    id = cur.fetchall()[0]['last_insert_rowid()']

    context = {
      "commentid": id,
      "lognameOwnsThis": True,
      "owner": logname,
      "text": text,
      "url": f"/api/v1/comments/{id}/"
    }

    return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/',  methods=['DELETE'])
def delete_comment(commentid):
    """Delete comment."""
    logname = authentication()
    connection = insta485.model.get_db()

    cur = connection.execute(
      "SELECT commentid, owner "
      "FROM comments "
      "WHERE commentid = ?",
      (commentid,)
    )

    comment = cur.fetchall()

    if len(comment) == 0:
        flask.abort(404)

    if comment[0]['owner'] != logname:
        flask.abort(403)

    connection.execute(
      "DELETE FROM comments WHERE commentid = ?",
      (commentid,)
    )

    return flask.jsonify({}), 204

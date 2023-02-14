"""REST API for posts."""
import flask
import hashlib
import insta485


# HELPER FUNCTIONS
def authentication():
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
      print("ABORTING")
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

  # HTTP Basic Access Authentication  
  #logname = flask.request.authorization['username']
  #password = flask.request.authorization['password']

  logname = authentication()
  connection = insta485.model.get_db()
  
  cur = connection.execute(
    "SELECT postid, owner, owner_img_url, img_url, timestamp "
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
    "ORDER BY timestamp, postid DESC ",
    (logname, logname)
  )
  postids = cur.fetchall()
  
  context = {"next": "", "results": []}
  print("DEBUG:", postids)
  for post in postids:
    curr_post = {'postid': post['postid'], 'url': '/api/v1/posts/{}/'.format(int(post['postid']))}
    context['results'].append(curr_post)
  
  context['url'] = '/api/v1/posts/'
  return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid"""

    logname = authentication()
    connection = insta485.model.get_db()

    #logname = flask.request.authorization['username']
    #password = flask.request.authorization['password']

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
    context['comments_url'] = '/api/v1/comments/?postid={}'.format(postid_url_slug)

    # Post and owner details
    cur = connection.execute(
      "SELECT P.created, P.filename as imgUrl, P.owner, U.filename as ownerImgUrl "
      "FROM posts P "
      "INNER JOIN users U ON P.owner = U.username "
      "WHERE P.postid = ? ",
      (postid_url_slug,)
    )
    post_dets = cur.fetchall()
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
      context['likes'] = {'lognameLikesThis': True, "numLikes": num_likes[0]['COUNT(*)'], 
                          'url': '/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
    else:
      context['likes'] = {'lognameLikesThis': False, "numLikes": num_likes[0]['COUNT(*)'], 
                          'url': None}

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
    context = {'likeid':likeid[0]['likeid'], 'url':'/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
    return flask.jsonify(**context), 201
  else:
    print("DEBUG: 200")
    context = {'likeid':likeid[0]['likeid'], 'url':'/api/v1/likes/{}/'.format(likeid[0]['likeid'])}
    return flask.jsonify(**context)
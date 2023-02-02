"""
Insta485 index (main) view.

URLs include:
/
"""

import uuid
import hashlib
import pathlib
import arrow
import flask
import insta485


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Need to figure out how to configure session control
    # Need to convert timestamp using arrow to make it usable
    # Figure out if more efficient way to do this is possible
    # How to configure missing uploads portion when rendering images
    # Need to figure out what's missing in like and comment forms
    # Add logname to render template dict

    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    # Query database
    logname = flask.session['username']
    # logname = "awdeorio"
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
        "ORDER BY timestamp, postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()

    for post in posts:
        # arrow.get(user['created'])
        coms = connection.execute(
            "SELECT C.owner, C.text "
            "FROM users U "
            "INNER JOIN posts P ON U.username = P.owner "
            "INNER JOIN comments C ON P.postid = C.postid "
            "WHERE U.username = ? AND P.postid = ? "
            "ORDER BY C.created, C.commentid ASC",
            (post['owner'], post['postid'])
        )
        comments = coms.fetchall()

        num_likes_q = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE postid = ?",
            (post['postid'],)
        )

        num_likes = num_likes_q.fetchall()
        # print(len(num_likes))
        post['likes'] = len(num_likes)

        like = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE owner = ? AND postid = ?",
            (logname, post['postid'])
        )

        like_flag = like.fetchall()
        if not like_flag:
            post['like_flag'] = 'false'
        else:
            post['like_flag'] = 'true'

        post['comments'] = comments
        timestamp = arrow.get(post['timestamp']).humanize()
        post['timestamp'] = timestamp

    # Add database info to context
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)


@insta485.app.route('/users/<user_url_slug>/')
def show_user(user_url_slug):
    """Show user page."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug,)
    )

    if not cur.fetchall():
        return flask.abort(404)

    logname = flask.session['username']
    context = {"logname": logname, "username": user_url_slug}
    follow = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, user_url_slug)
    )

    follow_arr = follow.fetchall()

    if not follow_arr:
        context["logname_follows_username"] = False
    else:
        context["logname_follows_username"] = True

    name = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug,)
    )

    fullname = name.fetchall()[0]['fullname']
    context['fullname'] = fullname

    num_following = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM following "
        "WHERE username1 = ? "
        "GROUP BY username1",
        (user_url_slug,)
    )

    following = num_following.fetchall()[0]['count']
    context['following'] = following

    num_followers = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM following "
        "WHERE username2 = ? "
        "GROUP BY username2",
        (user_url_slug,)
    )
    followers = num_followers.fetchall()[0]['count']
    context['followers'] = followers

    num_posts = connection.execute(
        "SELECT COUNT(*) AS count "
        "FROM posts "
        "WHERE owner = ? "
        "GROUP BY owner",
        (user_url_slug,)
    )
    total_posts = num_posts.fetchall()[0]['count']
    context['total_posts'] = total_posts

    post_obj = connection.execute(
        "SELECT P.postid, P.filename as img_url "
        "FROM users U "
        "INNER JOIN posts P ON U.username = P.owner "
        "WHERE U.username = ?",
        (user_url_slug,)
    )
    posts = post_obj.fetchall()
    context['posts'] = posts

    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<user_url_slug>/followers/')
def show_user_followers(user_url_slug):
    """Show followers page."""
    # Configure logname and images

    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    connection = insta485.model.get_db()

    logname = flask.session['username']
    context = {}
    context['logname'] = logname

    follower_q = connection.execute(
        "SELECT U.username, U.filename AS user_img_url "
        "FROM following F "
        "INNER JOIN users U ON F.username1 = U.username "
        "WHERE F.username2 = ?",
        (user_url_slug,)
    )
    followers = follower_q.fetchall()

    context['followers'] = followers
    for follower in followers:
        follow_q = connection.execute(
            "SELECT * "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, follower['username'])
        )
        follow = follow_q.fetchall()
        if not follow:
            follower['logname_follows_username'] = False
        else:
            follower['logname_follows_username'] = True

    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/')
def show_user_following(user_url_slug):
    """Show following page."""
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    connection = insta485.model.get_db()

    logname = flask.session['username']
    context = {}
    context['logname'] = logname
    context['user_url_slug'] = user_url_slug

    following_q = connection.execute(
        "SELECT U.username, U.filename AS user_img_url "
        "FROM following F "
        "INNER JOIN users U ON F.username2 = U.username "
        "WHERE F.username1 = ?",
        (user_url_slug,)
    )
    following = following_q.fetchall()

    context['following'] = following
    for follower in following:
        follow_q = connection.execute(
            "SELECT * "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, follower['username'])
        )
        follow = follow_q.fetchall()
        if not follow:
            follower['logname_follows_username'] = False
        else:
            follower['logname_follows_username'] = True

    return flask.render_template("following.html", **context)


@insta485.app.route('/following/', methods=['post'])
def post_follow():
    """POST for follow button."""
    connection = insta485.model.get_db()
    operation = flask.request.form['operation']
    target = flask.request.args.get('target')
    logname = flask.session['username']
    username = flask.request.form['username']
    # make logname and username declared by session
    if operation == 'follow':
        connection.execute(
            "INSERT INTO following(username1, username2, created) "
            "VALUES (?, ?, CURRENT_TIMESTAMP)",
            (logname, username)
        )
        # add unfollow option
        return flask.redirect(target)

    connection.execute(
        "DELETE FROM following WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )
    return flask.redirect(target)


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Show delete account page."""
    return flask.render_template("/accounts/delete.html",
                                 **{'logname': flask.session['username']})


@insta485.app.route('/accounts/login/')
def show_login():
    """Display login route."""
    return flask.render_template("/accounts/login.html")


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display login route."""
    connection = insta485.model.get_db()
    info = connection.execute(
        "SELECT username, filename, fullname, email "
        "FROM users "
        "WHERE username = ?",
        (flask.session['username'],)
    )

    return flask.render_template("/accounts/edit.html", **info.fetchall()[0])


@insta485.app.route('/accounts/password/')
def show_password():
    """Show password."""
    return flask.render_template("/accounts/password.html")


@insta485.app.route('/accounts/',  methods=['post'])
def post_account():
    """POST for account."""
    target = flask.request.args.get('target')
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    if operation == 'login':

        username = flask.request.form['username']

        cur = connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ?",
            (username,)
            )

        cur = cur.fetchall()
        if not cur:
            return flask.abort(403)

        password = cur[0]['password']

        try_password = flask.request.form['password']

        algorithm = 'sha512'
        salt = password.split('$')[1]
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + try_password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        try_password_db_string = "$".join([algorithm, salt, password_hash])

        if password == try_password_db_string:
            flask.session['username'] = flask.request.form['username']
            if target:
                return flask.redirect(target)
            return flask.redirect('/')

        return flask.abort(403)
    if operation == 'create':
        fullname = flask.request.form['fullname']

        username = flask.request.form['username']
        use = connection.execute(
            "SELECT * "
            "FROM users "
            "WHERE username = ?",
            (username,)
        )
        if use.fetchall():
            return flask.abort(409)

        email = flask.request.form['email']

        password = flask.request.form['password']
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        cur = connection.execute(
            "INSERT INTO users(username, fullname, email, "
            "filename, password, created) "
            "VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (username, fullname, email, filename, password_db_string)
        )

        flask.session['username'] = flask.request.form['username']
        if target:
            return flask.redirect(target)
        return flask.redirect(flask.url_for('show_index'))
    if operation == 'delete':

        posts_q = connection.execute(
            "SELECT filename "
            "FROM posts "
            "WHERE owner = ?",
            (flask.session['username'],)
        )

        posts = posts_q.fetchall()

        for post in posts:
            pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] /
                         post['filename']).unlink()

        connection.execute(
            "DELETE FROM users WHERE username = ?",
            (flask.session['username'],)
        )
        flask.session.pop('username')
        return flask.redirect(target)
    if operation == 'edit_account':
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']

        cur = connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username  = ?",
            (fullname, email, flask.session['username'])
        )

        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        if filename == '':
            pass
        else:
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"

            img = connection.execute(
                "UPDATE users "
                "SET filename = ? "
                "WHERE username = ?",
                (uuid_basename, flask.session['username'])
            )
        if target is not None:
            return flask.redirect(target)

        return flask.redirect(flask.url_for('show_index'))

    password = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']

    if new_password1 != new_password2:
        return flask.abort(400)

    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (flask.session['username'],)
    )
    ver_password = cur.fetchall()[0]['password']

    algorithm = 'sha512'
    salt = ver_password.split('$')[1]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    if ver_password != password_db_string:
        return flask.abort(403)

    algorithm2 = 'sha512'
    salt2 = uuid.uuid4().hex
    hash_obj2 = hashlib.new(algorithm2)
    password_salted2 = salt2 + new_password1
    hash_obj2.update(password_salted2.encode('utf-8'))
    password_hash2 = hash_obj2.hexdigest()
    password_db_string2 = "$".join([algorithm2, salt2, password_hash2])

    connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ?",
        (password_db_string2, flask.session['username'])
    )

    if target:
        return flask.redirect(target)

    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/explore/')
def show_explore():
    """Show explore."""
    connection = insta485.model.get_db()

    logname = flask.session['username']
    cur = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username != ? AND username NOT IN "
        "(SELECT username2 "
        "FROM following "
        "WHERE username1 == ?) ",
        (logname, logname)
    )

    not_following = cur.fetchall()
    context = {"logname": logname, "not_following": not_following}
    return flask.render_template("explore.html", **context)


# Add html configurations

@insta485.app.route('/posts/<postid_url_slug>/')
def show_post(postid_url_slug):
    """Show post page."""
    connection = insta485.model.get_db()

    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session['username']
    context = {}
    context['logname'] = logname

    post_q = connection.execute(
        "SELECT DISTINCT P.postid, P.owner, U.filename AS owner_img_url, "
        "P.filename AS img_url, P.created AS timestamp "
        "FROM posts P "
        "INNER JOIN users U ON P.owner = U.username "
        "WHERE P.postid = ? "
        "GROUP BY P.postid, P.owner, U.filename, P.filename, P.created",
        (postid_url_slug,)
    )

    post = post_q.fetchall()

    if not post:
        return flask.redirect(flask.url_for('show_login'))

    post = post[0]

    num_likes_q = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE postid = ?",
        (post['postid'],)
    )
    post['likes'] = len(num_likes_q.fetchall())

    log_likes_q = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid_url_slug)
    )

    log_likes = log_likes_q.fetchall()

    if log_likes:
        context['logname_likes_post'] = True
    else:
        context['logname_likes_post'] = False

    log_owns_q = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ? AND owner = ?",
        (postid_url_slug, logname)
    )

    log_owns = log_owns_q.fetchall()

    if log_owns:
        context['logname_own_post'] = True
    else:
        context['logname_own_post'] = False

    context['owner'] = post['owner']
    context['owner_img_url'] = post['owner_img_url']
    context['img_url'] = post['img_url']
    timestamp = arrow.get(post['timestamp']).humanize()
    context['timestamp'] = timestamp
    context['likes'] = post['likes']

    # Make sure to order by timestamp
    comments_q = connection.execute(
        "SELECT owner, text "
        "FROM comments "
        "WHERE postid = ? "
        "ORDER BY created, commentid ASC",
        (postid_url_slug,)
    )

    comments = comments_q.fetchall()
    context['comments'] = comments

    return flask.render_template("post.html", **context)


@insta485.app.route('/uploads/<img_url>')
def show_image(img_url):
    """Show images."""
    if 'username' not in flask.session:
        return flask.abort(403)

    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     img_url, as_attachment=True)


@insta485.app.route('/accounts/create/')
def show_create():
    """Show create page."""
    if 'username' in flask.session:
        return flask.redirect('/accounts/edit/')
    return flask.render_template("accounts/create.html/")


@insta485.app.route('/accounts/logout/', methods=['post'])
def logout():
    """logout."""
    del flask.session['username']
    return flask.redirect('/accounts/login/')


@insta485.app.route('/likes/', methods=['post'])
def likes():
    """Like or unlike a post."""
    target = flask.request.args.get("target")
    operation = flask.request.form['operation']
    postid = flask.request.form['postid']
    if target is None:
        target = '/'

    connection = insta485.model.get_db()

    if operation == 'like':
        # Check if user already liked
        cur = connection.execute(
            "SELECT owner, postid "
            "FROM likes "
            "WHERE owner = ? AND postid = ?",
            (flask.session['username'], postid)
        )
        user_likes = cur.fetchall()
        if len(user_likes) != 0:
            return flask.abort(409)

        # like post
        cur = connection.execute(
            "INSERT INTO likes(owner, postid, created) "
            "VALUES (?, ?, CURRENT_TIMESTAMP) ",
            (flask.session['username'], postid)
        )
        return flask.redirect(target)

    # Check if user already unliked
    cur = connection.execute(
        "SELECT owner, postid "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (flask.session['username'], postid)
    )
    user_likes = cur.fetchall()
    if len(user_likes) == 0:
        return flask.abort(409)

    # unlike post
    cur = connection.execute(
        "DELETE FROM likes "
        "WHERE owner = ? AND postid = ?",
        (flask.session['username'], postid)
    )
    return flask.redirect(target)


@insta485.app.route('/comments/',  methods=['POST'])
def post_comments():
    """POST comments."""
    operation = flask.request.form['operation']
    target = flask.request.args.get('target')
    username = flask.session['username']
    if target is None:
        target = '/'
    connection = insta485.model.get_db()

    if operation == 'create':
        postid = flask.request.form['postid']
        text = flask.request.form["text"]
        if text == "":
            return flask.abort(400)

        cur = connection.execute(
            "INSERT INTO comments(owner, postid, text, created)"
            "VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (username, postid, text)
        )
        return flask.redirect(target)

    commentid = flask.request.form['commentid']

    connection.execute(
        "DELETE FROM comments "
        "WHERE commentid = ?",
        (commentid,)
    )

    return flask.redirect(target)


@insta485.app.route('/posts/',  methods=['POST'])
def post_post():
    """POST post."""
    operation = flask.request.form['operation']

    target = flask.request.args.get('target')
    user_in = flask.session['username']

    connection = insta485.model.get_db()

    if target is None:
        target = f'/users/{user_in}/'
    target = f'/users/{user_in}/'

    if operation == 'create':

        postid = flask.request.form['create_post']

        fileobj = flask.request.files["file"]
        if not fileobj:
            return flask.abort(400)

        filename = fileobj.filename
        # Compute base name (filename without directory).We use a UUID to avoid
        # clashes with existing files, and ensure that the name is compatible
        # with the filesystem. For best practive, we ensure uniform file
        # extensions (e.g. lowercase).
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts(filename, owner, created) "
            "VALUES (?, ?, CURRENT_TIMESTAMP)",
            (uuid_basename, user_in)
        )

        return flask.redirect(target)

    postid = flask.request.form['postid']
    logname = flask.session['username']

    cur = connection.execute(
        "SELECT filename, owner "
        "FROM posts "
        "WHERE postid = ?",
        (postid,)
    )

    info = cur.fetchall()[0]

    if info['owner'] != logname:
        return flask.abort(403)

    connection.execute(
        "DELETE FROM posts "
        "WHERE postid = ?",
        (postid,)
    )

    post = info['filename']

    pathlib.Path(insta485.app.config["UPLOAD_FOLDER"]/post).unlink()

    if target:
        return flask.redirect(target)

    return flask.redirect('/')

"""REST API for posts."""
import flask
import insta485


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
  logname = flask.session['username']
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
    "ORDER BY timestamp, postid DESC",
    (logname, logname)
  )
  postids = cur.fetchall()
  
  context = {"next": "", "results": []}
  print("DEBUG:", postids)
  for post in postids:
    curr_post = {'postid': post['postid'], 'url': '/api/v1/posts/{}/'.format(post['postid'])}
    context['results'].append(curr_post)
  
  context['url'] = '/api/v1/posts/'
  return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    # CHANGE THIS TO NOT BE HARD CODED
    """Return post on postid.

    Example:
    {
    "created": "2017-09-28 04:33:28",
    "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
    "owner": "awdeorio",
    "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
    "ownerShowUrl": "/users/awdeorio/",
    "postShowUrl": "/posts/1/",
    "url": "/api/v1/posts/1/"
    }
    """
    context = {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postid": "/posts/{}/".format(postid_url_slug),
      "url": flask.request.path,
    }
    return flask.jsonify(**context)

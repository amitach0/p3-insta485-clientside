import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import LikesButton from "./likes.jsx";
import Comment from "./comments.jsx";
import moment from "moment";
//import UnlikeButton from "./unlikebutton.jsx";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [numLikes, setLikes] = useState("");
  const [lognamelikes, setlognameLikes] = useState("");
  const [likeUrl, setLikesUrl] = useState("");
  const [comments, setComments] = useState([]);
  const [created, setCreated] = useState("");
  const [postUrl, setPostUrl] = useState("");
  const [postId, setPostId] = useState("");
  const [textEntry, setTextEntry] = useState("");

  function unlike() {
    //useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    fetch(likeUrl, { method: "DELETE" }, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        //return response.json();
      })
      .then(() => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setlognameLikes(false);
          setLikes((prevVal) => {
            return prevVal - 1;
          });
          setLikesUrl(null);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
    //}, [likeUrl]);
  }

  function like() {
    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    let url = "/api/v1/likes/?postid=" + postId;

    fetch(url, { method: "POST" }, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setlognameLikes(true);
          setLikes((prevVal) => {
            return prevVal + 1;
          });
          setLikesUrl(data.url);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }

  const handleSubmit = (event) => {
    //setName(textEntry);
    //prevents website from refreshing (default action of form submission)
    event.preventDefault();
  };

  function handleComment(e) {
    console.log(e);
    e.preventDefault();

    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    let url = "/api/v1/comments/?postid=" + postId;

    fetch(
      url,
      {
        method: "POST",
        headers: { "Content-Type": "applications/json" },
        body: JSON.stringify({ text: e.target.value }),
      },
      { credentials: "same-origin" }
    )
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          const newComment = (
            <p>
              <b>{owner}</b> {e.target.value}
            </p>
          );
          commentsList([...commentsList, ...newComment]);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setLikes(data.likes["numLikes"]);
          setlognameLikes(data.likes["lognameLikesThis"]);
          setLikesUrl(data.likes["url"]);
          setComments(data.comments);
          setOwnerShowUrl(data.ownerShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setCreated(data.created);
          setPostUrl(data.postShowUrl);
          setPostId(data.postid);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const commentsList = comments.map((comment) => (
    <p>
      <b>{comment.owner}</b> {comment.text}
    </p>
  ));

  // Render post image and post owner
  return (
    <div className="post">
      <h3>
        <a href={ownerShowUrl}>
          <img src={ownerImgUrl} alt="profile_image" />
        </a>
        <a href={ownerShowUrl}>
          <b>{owner}</b>
        </a>
      </h3>
      <h3>
        <a href={postUrl}>{moment.utc(created).fromNow()}</a>
      </h3>
      <img src={imgUrl} alt="post_image" />
      {lognamelikes == true ? (
        <LikesButton
          clickHandler={() => {
            unlike();
          }}
          name="unlike"
        />
      ) : (
        <LikesButton
          clickHandler={() => {
            like();
          }}
          name="like"
        />
      )}
      <p>
        {numLikes} {numLikes == 1 ? "like" : "likes"}
      </p>

      <span className="comment-text">{commentsList}</span>
      <form className="comment-form" onSubmit={handleComment}>
        <input type="text" name="text" />
      </form>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

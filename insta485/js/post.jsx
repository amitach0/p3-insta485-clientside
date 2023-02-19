import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import moment from "moment";
import LikesButton from "./likes";
import CommentButton from "./comments";

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
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    fetch(likeUrl, { method: "DELETE" }, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .then(() => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setlognameLikes(false);
          setLikesUrl(null);
          setLikes((prevVal) => prevVal - 1);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
    // }, [likeUrl]);
  }

  function like() {
    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    const likesUrl = `/api/v1/likes/?postid=${postId}`;

    fetch(likesUrl, { method: "POST" }, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setlognameLikes(true);
          setLikes((prevVal) => prevVal + 1);
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

  const handleChange = (event) => {
    setTextEntry(event.target.value);
    // console.log(event.target.value);
  };

  const doubleclick = () => {
    console.log("attempt");
    console.log(lognamelikes);
    if (!lognamelikes) {
      like();
    }
  };

  function handleComment(e) {
    // console.log(e);
    // console.log(e.target.action);

    let ignoreStaleRequest = false;
    // Call REST API to get the post's information

    // const postUrl = "/api/v1/comments/?postid=" + postId;
    const commentUrl = `/api/v1/comments/?postid=${postId}`;

    fetch(
      commentUrl,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textEntry }),
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
          /* const newComment = (
            <p>
              <b>{owner}</b> {textEntry}
            </p>
          );
          commentsList([...commentsList, ...newComment]); */
          setComments((prevVal) => prevVal.concat(data));
        }
      })
      .catch((error) => console.log(error));

    setTextEntry("");
    e.preventDefault();

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }

  function deleteComment(deleteUrl) {
    let ignoreStaleRequest = false;
    fetch(deleteUrl, { method: "DELETE" }, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // return response.json();
      })
      .then(() => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setComments((prevVal) =>
            prevVal.filter((comment) => comment.url !== deleteUrl)
          );
          // setCommentUrl(null);
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
          setLikes(data.likes.numLikes);
          setlognameLikes(data.likes.lognameLikesThis);
          setLikesUrl(data.likes.url);
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
    <p key={comment.url}>
      <a href={comment.ownerShowUrl}>{comment.owner}</a> {comment.text}{" "}
      {comment.lognameOwnsThis ? (
        <CommentButton
          clickHandler={() => {
            deleteComment(comment.url);
          }}
        />
      ) : (
        ""
      )}
    </p>
  ));

  // Render post image and post owner
  if (imgUrl !== "") {
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
        <img
          onDoubleClick={() => doubleclick()}
          src={imgUrl}
          alt="post_image"
        />
        <p>
          {lognamelikes === true ? (
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
        </p>
        <p>
          {numLikes} {numLikes === 1 ? "like" : "likes"}
        </p>

        <span className="comment-text">{commentsList}</span>
        <form className="comment-form" onSubmit={handleComment}>
          <input
            type="text"
            name="text"
            value={textEntry}
            onChange={handleChange}
          />
        </form>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

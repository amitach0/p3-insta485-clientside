import React from "react";

export default function CommentButton(props) {
  return (
    <button
      className="delete-comment-button"
      onClick={() => {
        props.clickHandler();
      }}
    >
      delete
    </button>
  );
}

import React from "react";

export default function CommentButton(props) {
  //const { clickHandler } = props;
  return (
    <button
      type="button"
      className="delete-comment-button"
      onClick={() => {
        {
          props.clickHandler();
        }
      }}
    >
      delete
    </button>
  );
}

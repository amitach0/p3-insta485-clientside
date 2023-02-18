import React, { useState } from "react";
import PropTypes from "prop-types";

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

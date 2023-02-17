import React, { useState } from "react";
import PropTypes from "prop-types";

export default function Comment({ comments }) {
  const commentsList = comments.map((comment) => (
    <p>
      <b>{comment.owner}</b> {comment.text}
    </p>
  ));

  return (
    <div className="comment">
      <ul>{commentsList}</ul>
    </div>
  );
}

Comment.propTypes = {
  comments: PropTypes.array.isRequired,
};

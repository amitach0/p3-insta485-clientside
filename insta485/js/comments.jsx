import React from "react";
import PropTypes from "prop-types";

export default function CommentButton({ clickHandler }) {
  return (
    <button
      type="button"
      className="delete-comment-button"
      onClick={clickHandler}
    >
      delete
    </button>
  );
}

CommentButton.propTypes = {
  clickHandler: PropTypes.func.isRequired,
};

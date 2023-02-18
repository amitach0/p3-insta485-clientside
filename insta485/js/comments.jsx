import React, { useState } from "react";
import PropTypes from "prop-types";

export default function Comment({ props }) {
  return (
    <div className="comment">
      <form
        className="comment-form"
        onSubmit={() => {
          props.clickHandler();
        }}
      >
        <input type="text" value="hello" />
      </form>
    </div>
  );
}

Comment.propTypes = {
  comments: PropTypes.array.isRequired,
};

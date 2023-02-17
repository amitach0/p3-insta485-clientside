import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";

export default function Likes({ numLikes }) {
  //const [lognameLikesThis, setLognameLThis] = useState("");
  //const [numLikes, setLikes] = useState("");

  return (
    <div className="likes">
      <p>{numLikes} likes</p>
    </div>
  );
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
};

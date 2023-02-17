import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";

export default function Likes({ numLikes, lognamelikes, url}) {
  const [lognameLikesThis, setLognameLThis] = useState(lognameLikesThis);
  const [likesNum, setLikes] = useState(numLikes);



  /*useEffect(() => { 
    let ignoreStaleRequest = false;

    

  }, [numLikes, lognamelikes, url]);*/

  if(lognamelikes == true){
    return (
      <div className="likes">
        <button> like </button>
        <p>{numLikes} likes</p>
      </div>
    )
  }
  else{
    return (
      <div className="likes">
          <button> unlike </button>
          <p>{numLikes} likes</p>
      </div>
    )
  }

  return (
    <div className="likes">
      <p>{numLikes} likes</p>
    </div>
  );
}

Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  lognamelikes: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
};

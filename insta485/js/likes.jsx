import PropTypes from "prop-types";
import React from "react";

export default function LikesButton({ name, clickHandler }) {
  // const { name } = props;
  return (
    <button type="button" className="like-unlike-button" onClick={clickHandler}>
      {name}
    </button>
  );
}

LikesButton.propTypes = {
  clickHandler: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
};

/* const [lognameLikesThis, setLognameLikesThis] = useState(lognamelikes);
  const [likesNum, setLikes] = useState(numLikes);
  console.log(lognameLikesThis)


  function unlike(){
    useEffect(() => {
      // Declare a boolean flag that we can use to cancel the API request.
      let ignoreStaleRequest = false;
  
      // Call REST API to get the post's information
      fetch(url, { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then(() => {
          // If ignoreStaleRequest was set to true, we want to ignore the results of the
          // the request. Otherwise, update the state to trigger a new render.
          if (!ignoreStaleRequest) {
            setLognameLikesThis(false)
            setLikes((prevVal) => {
              return prevVal - 1;
            });
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
  }

  if(lognamelikes == true){
    return (
      <div className="likes">
        <button onClick={unlike}> unlike </button>
        <p>{numLikes} likes</p>
      </div>
    )
  }
  else{
    return (
      <div className="likes">
          <button> like </button>
          <p>{numLikes} likes</p>
      </div>
    )
  }

  return (
    <div className="likes">
      <p>{numLikes} likes</p>
    </div>
  ); */

/*
Likes.propTypes = {
  numLikes: PropTypes.number.isRequired,
  lognamelikes: PropTypes.bool.isRequired,
  url: PropTypes.string.isRequired,
};
*/

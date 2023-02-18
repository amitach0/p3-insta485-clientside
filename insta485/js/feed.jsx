import React, { useState, useEffect } from "react";
import Post from "./post.jsx";
import InfiniteScroll from "react-infinite-scroll-component";
//import { render } from "react-dom";
//import { data } from "cypress/types/jquery/index.js";

import PropTypes from "prop-types";

export default function Feed({ url }) {
  const [results, setResults] = useState([]);
  const [next, setNext] = useState("");

  // posts, nextUrl,

  //const [next, getNext] = use

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
          setResults(data.results);
          setNext(data.next);
          console.log(data.results);
          console.log(results);
          //store url to get next 10
          //one
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
  const fetchMore = () => {
    console.log(url);
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setResults([...data.results, ...data.next]);

        //spread operator
        // add new posts
      })
      .catch((error) => console.log(error));
  };

  //console.log(results);

  const postsList = results.map((post) => (
    <Post url={post["url"]} key={post["url"]} />
  ));

  return (
    <div className="feed">
      <InfiniteScroll
        dataLength={results.length}
        next={fetchMore}
        hasMore={true}
        loader={<h4>Loading...</h4>}
      >
        <span>{postsList}</span>
      </InfiniteScroll>
    </div>
  );

  /*


 return (

    <div className="feed">
      <ul>{postsList}</ul>
    </div>
  );
  */
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

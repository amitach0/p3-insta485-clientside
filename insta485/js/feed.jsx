import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import PropTypes from "prop-types";
import Post from "./post";

export default function Feed({ url }) {
  const [results, setResults] = useState([]);
  const [next, setNext] = useState("");

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
    console.log(next);
    fetch(next, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log(results);
        console.log(data.results);
        setResults([...results, ...data.results]);
        setNext(data.next);
      })
      .catch((error) => console.log(error));
  };

  const postsList = results.map((post) => (
    <Post url={post.url} key={post.postid} />
  ));

  return (
    <div className="feed">
      <InfiniteScroll
        dataLength={results.length}
        next={fetchMore}
        hasMore
        loader={<h4>Loading...</h4>}
      >
        <span>{postsList}</span>
      </InfiniteScroll>
    </div>
  );
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

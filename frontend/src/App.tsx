import React, { useEffect, useState } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import logo from "./logo.svg";
import "./App.css";
import Api from "./services/Api";
import ScatterGraph from "./components/graphs/ScatterGraph";
import LineGraph from "./components/graphs/LineGraph";

const App = () => {
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("Loading...");
  const [data, setData] = useState([]);
  const [query, setQuery] = useState("victoria beckham");
  useEffect(() => {
    Api.post("count-interval", {
      query: query,
      interval_mins: 60*24,
      days_ago: 360,
    }).then((res) => {
      console.log(res);
      console.log(res[0]);
      setData(res);
      setLoading(false);
    });
  }, []);
  return (
    <div className="App">
      <header className="App-header">
        {loading ? (
          text
        ) : (
          <LineGraph data={data} xLabel={"Time"} yLabel={"Count"} zLabel={"Query"} title={query}/>
        )}
      </header>
    </div>
  );
};

export default App;

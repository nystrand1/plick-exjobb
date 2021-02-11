import React, { useEffect, useState } from "react";
// @ts-ignore
import DateTimePicker from "react-datetime-picker"
import logo from "./logo.svg";
import "./App.scss";
import Api from "./services/Api";
import ScatterGraph from "./components/graphs/ScatterGraph";
import LineGraph from "./components/graphs/LineGraph";

const App = () => {
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("Loading...");
  const [data, setData] = useState([]);
  const [query, setQuery] = useState("sommar%");
  const [startDate, setStartDate] = useState(new Date("2021-01-04"));
  const [endDate, setEndDate] = useState(new Date("2021-01-05"));
  useEffect(() => {
    Api.countIntervalIndividual({
      query: query,
      interval_mins: 60,
      start_date: startDate,
      end_date: endDate,
    }).then((res) => {
      console.log(res);
      setData(res);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    Api.countIntervalIndividual({
      query: query,
      interval_mins: 60,
      start_date: startDate,
      end_date: endDate,
    }).then((res) => {
      console.log(res);
      setData(res);
      setLoading(false);
    });
  }, [startDate, endDate]);

  return (
    <div className="App">
      <header className="App-header">
        <div>
        {loading ? (
          text
        ) : (
          <LineGraph data={data} xLabel={"Time"} yLabel={"Count"} zLabel={"Query"} title={query}/>
        )}
        <DateTimePicker onChange={setStartDate} value={startDate}/>
        <DateTimePicker onChange={setEndDate} value={endDate}/>
        </div>
      </header>
    </div>
  );
};

export default App;

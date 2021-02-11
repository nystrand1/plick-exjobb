import React, { useEffect, useState } from "react";
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    Legend,
  } from "recharts";

  export interface ScatterGraphProps {
    title : string,
    xLabel : string,
    yLabel : string,
    zLabel? : string,
    data : any
  }

  const ScatterGraph = (props : ScatterGraphProps) => {

    const {data, xLabel, yLabel, zLabel, title} = props;
    return (
    <ScatterChart
        width={1400}
        height={900}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey={"time_interval"}
          name={xLabel}
          style={{ fontSize: 14 }}
          type={"category"}
        />
        <YAxis dataKey={"count"} name={yLabel} />
        <Scatter
          className={"scatter"}
          name={title}
          data={data}
          fill="#8884d8"
          style={{ fontSize: 14 }}
        />
        <ZAxis dataKey={"query"} name={zLabel} />
        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
        <Legend />
      </ScatterChart>
    );
  }
  
  export default ScatterGraph;
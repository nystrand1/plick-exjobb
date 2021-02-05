import React, { useEffect, useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    ZAxis,
    CartesianGrid,
    Tooltip,
    Legend,
  } from "recharts";

  export interface LineGraphProps {
    title : string,
    xLabel : string,
    yLabel : string,
    zLabel? : string,
    data : any
  }

  const LineGraph = (props : LineGraphProps) => {

    const {data, xLabel, yLabel, zLabel, title} = props;
    return (
    <LineChart
        width={1400}
        height={900}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        data={data}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey={"time"}
          style={{ fontSize: 14 }}
        />
        <YAxis name={yLabel} />
        <ZAxis dataKey={"query"} name={zLabel} />
        <Line
          type="monotone"
          name={title}
          dataKey={"count"}
          style={{ fontSize: 14 }}
        />
        <Tooltip labelStyle={{color: "black"}}/>
        <Legend />
      </LineChart>
    );
  }
  
  export default LineGraph;
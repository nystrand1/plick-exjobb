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
  import CustomTooltip from "../misc/CustomToolTip/CustomToolTip";

  export interface LineGraphProps {
    title : string,
    xLabel : string,
    yLabel : string,
    zLabel? : string,
    data : any,
    futureData? : any,
  }

  const LineGraph = (props : LineGraphProps) => {

    const {data, xLabel, yLabel, zLabel, title, futureData} = props;

    return (
    <LineChart
        width={1400}
        height={900}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        data={data}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey={"time_interval"}
          style={{ fontSize: 14 }}
        />
        <YAxis name={yLabel} />
        <ZAxis dataKey={"query"}/>
        <Line
          type="monotone"
          name={title}
          dataKey={"count"}
          style={{ fontSize: 14 }}
        />
        <Tooltip labelStyle={{color: "black"}} content={<CustomTooltip fallBackName={title} />}/>
        <Legend />
      </LineChart>
    );
  }
  
  export default LineGraph;
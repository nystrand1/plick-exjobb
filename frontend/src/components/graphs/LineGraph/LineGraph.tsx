import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { CustomTooltip } from '~components'

export interface LineGraphProps {
  title: string
  xLabel: string
  yLabel: string
  zLabel?: string
  data: any
  futureData?: any
}

export const LineGraph = (props: LineGraphProps) => {
  const { data, yLabel, title } = props

  const colors = ["yellow", "blue", "green", "pink", "purple"]

  const getTrendlines = () => {
    if (data[0].trends == null) return;
    return Object.keys(data[0]?.trends).filter(key => key?.startsWith("degree")); 
  }

  return (
    <LineChart
      width={1400}
      height={900}
      margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      data={data}
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey={'time_interval'} style={{ fontSize: 14 }} />
      <YAxis name={yLabel} />
      <ZAxis dataKey={'query'} />
      <Line
        type="monotone"
        name={title}
        dataKey={'count'}
        style={{ fontSize: 14 }}
        fill="red"
        stroke="red"
      />
      {getTrendlines()?.map((key, i) => {
        return <Line
        key={key}
        type="monotone"
        name={key}
        dataKey={`trends.${key}`}
        style={{ fontSize: 14 }}
        fill={colors[i % colors.length]}
        stroke={colors[i % colors.length]}
      />
      })}
      <Tooltip
        labelStyle={{ color: 'black' }}
        content={<CustomTooltip fallBackName={title} />}
      />
      <Legend />
    </LineChart>
  )
}

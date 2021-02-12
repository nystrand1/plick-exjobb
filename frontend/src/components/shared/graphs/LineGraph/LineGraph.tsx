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
      <Line
        type="monotone"
        name={'trend'}
        dataKey={'trend'}
        style={{ fontSize: 14 }}
        fill="green"
        stroke="green"
      />
      <Tooltip
        labelStyle={{ color: 'black' }}
        content={<CustomTooltip fallBackName={title} />}
      />
      <Legend />
    </LineChart>
  )
}

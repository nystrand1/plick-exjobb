import * as React from 'react'
import s from './LineGraph.module.scss'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
import { colors } from '~utils'

interface LineGraphProps {
  width: number
  height: number
}

export const LineGraph = ({ width, height }: LineGraphProps) => {
  const data = [
    {
      name: 'Page A',
      uv: 4000,
      pv: 2400,
      amt: 2400,
    },
    {
      name: 'Page B',
      uv: 3000,
      pv: 1398,
      amt: 2210,
    },
    {
      name: 'Page C',
      uv: 2000,
      pv: 9800,
      amt: 2290,
    },
    {
      name: 'Page D',
      uv: 2780,
      pv: 3908,
      amt: 2000,
    },
    {
      name: 'Page E',
      uv: 1890,
      pv: 4800,
      amt: 2181,
    },
    {
      name: 'Page F',
      uv: 2390,
      pv: 3800,
      amt: 2500,
    },
    {
      name: 'Page G',
      uv: 3490,
      pv: 4300,
      amt: 2100,
    },
  ]

  const margin = 50

  return (
    <div className={s.lineGraphWrapper}>
      <LineChart
        width={width}
        height={height}
        data={data}
        margin={{ top: margin / 5, right: margin, left: margin / 2, bottom: margin / 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="pv" stroke={colors[1]} strokeWidth={3} />
        <Line type="monotone" dataKey="uv" stroke={colors[2]} strokeWidth={3} />
      </LineChart>
    </div>
  )
}

import * as React from 'react'
import s from './LineGraph.module.scss'
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
import moment from 'moment'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { CustomTooltip } from '../CustomToolTip'

interface LineGraphProps {
  width: number
  height: number
}

export const LineGraph = ({ width, height }: LineGraphProps) => {
  const { activeLines, timeSeriesSerachTerms, resolution } = useContext()
  const [data, setData] = React.useState<ITimeSeriesSearchTerms[]>([])
  const margin = 50

  React.useEffect(() => {
    setData(timeSeriesSerachTerms.filter((data) => activeLines.includes(data.query)))
  }, [setData, activeLines, timeSeriesSerachTerms])

  const getData = () => {
    const res: any[] = []
    data.forEach((entry) => {
      switch (resolution) {
        case 'day':
          res.push(
            ...entry.time_series_day.map((o) => {
              let dataPoint = {}
              dataPoint[`count_${entry.query}`] = o.count
              dataPoint['time_interval'] = o.time_interval
              dataPoint['trends'] = o.trends
              return dataPoint
            }),
          )
          break
        case 'week':
          return entry.time_series_week
        case 'month':
          return entry.time_series_month
      }
    })
    console.log(res)
    return res
  }

  console.log(data)

  const xAxisTickFormatter = (date) => {
    return moment(date, 'YYYY-MM-DD hh:mm:ss').format('YYYY-MM-DD')
  }

  if (data.length < 1) {
    return <div className={s.textWrapper}>Välj i listan för att visa värden</div>
  }

  return (
    <div className={s.lineGraphWrapper}>
      <LineChart
        width={width}
        height={height}
        data={getData()}
        margin={{ top: margin / 5, right: margin, left: margin / 2, bottom: margin / 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey={'time_interval'}
          style={{ fontSize: 14 }}
          tickFormatter={xAxisTickFormatter}
        />
        <YAxis name={'count'} />
        <ZAxis dataKey={'query'} />
        <Tooltip content={<CustomTooltip tickFormatter={xAxisTickFormatter} />} />
        <Legend />
        <Line
          type="monotone"
          dataKey="count_ganni"
          stroke={colors[0]}
          strokeWidth={3}
          dot={false}
        />
      </LineChart>
    </div>
  )
}

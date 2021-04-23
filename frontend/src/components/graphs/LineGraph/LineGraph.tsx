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
import { Api } from '~services'
import { CustomTooltip } from '../CustomToolTip'

interface LineGraphProps {
  width: number
  height: number
}

export const LineGraph = ({ width, height }: LineGraphProps) => {
  const {
    activeLines,
    resolution,
    topListBrands,
    topListCategories,
    activeType,
    startDate,
    endDate,
  } = useContext()
  const [data, setData] = React.useState<ITimeSeriesSearchTerms[]>([])
  const margin = 50

  React.useEffect(() => {
    if (activeLines.length > 0) {
      switch (activeType) {
        case 'brand':
          Api.getBrandTimeseries({
            brand_ids: activeLines,
            resolution: resolution,
          }).then((data) => {
            const startIndex = data.findIndex(
              (e) => Number(new Date(e.time_interval)) === Number(startDate),
            )
            const endIndex =
              data.findIndex(
                (e) => Number(new Date(e.time_interval)) === Number(endDate),
              ) + 1
            setData(data.slice(startIndex > 0 ? startIndex : 0, endIndex || data.length))
          })
          break

        case 'category':
          Api.getCategoryTimeseries({
            category_ids: activeLines,
            resolution: resolution,
          }).then((data) => {
            const startIndex = data.findIndex(
              (e) => Number(new Date(e.time_interval)) === Number(startDate),
            )
            const endIndex =
              data.findIndex(
                (e) => Number(new Date(e.time_interval)) === Number(endDate),
              ) + 1
            setData(data.slice(startIndex > 0 ? startIndex : 0, endIndex || data.length))
          })
          break

        case 'query':
          Api.getQueryTimeseries({
            query_ids: ['nike'],
            resolution: resolution,
          }).then((data) => {
            const startIndex = data.findIndex(
              (e) => Number(new Date(e.time_interval)) === Number(startDate),
            )
            const endIndex =
              data.findIndex(
                (e) => Number(new Date(e.time_interval)) === Number(endDate),
              ) + 1
            setData(data.slice(startIndex > 0 ? startIndex : 0, endIndex || data.length))
          })
          break
      }
    }
  }, [setData, activeLines, resolution, startDate, endDate, activeType])

  React.useEffect(() => {
    setData([])
  }, [activeType])

  const getColorIndex = (lineId: number) => {
    switch (activeType) {
      case 'brand':
        return topListBrands?.findIndex((element) => element.brand_id === lineId) || 0

      case 'category':
        return (
          topListCategories?.findIndex((element) => element.category_id === lineId) || 0
        )

      default:
        return 0
    }
  }

  const xAxisTickFormatter = (date) => {
    return moment(date, 'YYYY-MM-DD hh:mm:ss').format('YYYY-MM-DD')
  }

  if (data.length < 1) {
    return <div className={s.textWrapper}>Välj i listan för att visa värden</div>
  }

  console.log(data)
  return (
    <div className={s.lineGraphWrapper}>
      <LineChart
        width={width}
        height={height}
        data={data}
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
        <Tooltip />
        <Legend />
        {activeLines.map((lineId) => (
          <Line
            key={lineId}
            type="monotone"
            dataKey={`${activeType}_${lineId}_count`}
            stroke={colors[getColorIndex(lineId)]}
            strokeWidth={3}
            dot={false}
          />
        ))}
      </LineChart>
    </div>
  )
}

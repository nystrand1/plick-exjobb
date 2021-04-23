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
    activeBrands,
    activeCategories,
    activeQueries,
    resolution,
    topListBrands,
    topListCategories,
    topListQueries,
    activeType,
    startDate,
    endDate,
  } = useContext()
  const [data, setData] = React.useState<ITimeSeriesSearchTerms[]>([])
  const margin = 50

  const sliceData = React.useCallback(
    (data) => {
      const startIndex = data.findIndex(
        (e) => Number(new Date(e.time_interval)) === Number(startDate),
      )
      const endIndex =
        data.findIndex((e) => Number(new Date(e.time_interval)) === Number(endDate)) + 1
      return data.slice(startIndex > 0 ? startIndex : 0, endIndex || data.length)
    },
    [endDate, startDate],
  )

  React.useEffect(() => {
    switch (activeType) {
      case 'brand':
        Api.getBrandTimeseries({
          brand_ids: activeBrands,
          resolution: resolution,
        }).then((data) => {
          setData(sliceData(data))
        })
        break

      case 'category':
        Api.getCategoryTimeseries({
          category_ids: activeCategories,
          resolution: resolution,
        }).then((data) => {
          setData(sliceData(data))
        })
        break

      case 'query':
        Api.getQueryTimeseries({
          query_ids: activeQueries,
          resolution: resolution,
        }).then((data) => {
          setData(sliceData(data))
        })
        break
    }
  }, [
    setData,
    activeBrands,
    activeCategories,
    activeQueries,
    resolution,
    startDate,
    endDate,
    activeType,
    sliceData,
  ])

  const getColorIndex = (lineId) => {
    switch (activeType) {
      case 'brand':
        return topListBrands?.findIndex((element) => element.brand_id === lineId) || 0

      case 'category':
        return (
          topListCategories?.findIndex((element) => element.category_id === lineId) || 0
        )

      case 'query':
        return topListQueries?.findIndex((element) => element.query === lineId) || 0

      default:
        return 0
    }
  }

  const getActiveLines = () => {
    switch (activeType) {
      case 'brand':
        return activeBrands
      case 'category':
        return activeCategories
      case 'query':
      default:
        return activeQueries
    }
  }

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
        {(getActiveLines() as Array<string | number>).map((lineId: string | number) => (
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

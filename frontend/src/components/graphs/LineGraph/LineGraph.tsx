import * as React from 'react'
import s from './LineGraph.module.scss'
import { LineChart, Line, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip } from 'recharts'
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
    activeLines,
  } = useContext()
  const [data, setData] = React.useState<ITimeSeriesSearchTerms[]>([])
  const [tcnData, setTcnData] = React.useState<ITimeSeriesSearchTerms[]>([])
  const margin = 50

  const updateData = React.useCallback(
    (data) => {
      const startIndex = data.findIndex(
        (e) => Number(new Date(e.time_interval)) === Number(startDate),
      )

      const tcnIndex = data.findIndex((d) =>
        Object.keys(d).find((key) => /tcn_pred_*/.test(key)),
      )

      if (tcnIndex) {
        setTcnData(data.slice(tcnIndex, data.length))
        data = data.slice(startIndex, tcnIndex)
      }

      const endIndex =
        data.findIndex((e) => Number(new Date(e.time_interval)) === Number(endDate)) + 1

      setData(data.slice(startIndex > 0 ? startIndex : 0, endIndex || data.length))
    },
    [endDate, startDate],
  )

  React.useEffect(() => {
    switch (activeType) {
      case 'brand':
        if (activeBrands.length > 0) {
          Api.getBrandTimeseries({
            brand_ids:
              activeBrands.length > 0
                ? activeBrands.map((line) => line.lineId as number)
                : [],
            resolution: resolution,
          }).then((data) => {
            updateData(data)
          })
        }
        break

      case 'category':
        if (activeCategories.length > 0) {
          Api.getCategoryTimeseries({
            category_ids:
              activeCategories.length > 0
                ? activeCategories.map((line) => line.lineId as number)
                : [],
            resolution: resolution,
          }).then((data) => {
            updateData(data)
          })
        }
        break

      case 'query':
        if (activeQueries.length > 0) {
          Api.getQueryTimeseries({
            query_ids:
              activeQueries.length > 0
                ? activeQueries.map((line) => line.lineId as string)
                : [],
            resolution: resolution,
          }).then((data) => {
            updateData(data)
          })
        }
        break
    }
  }, [
    activeBrands,
    activeCategories,
    activeQueries,
    resolution,
    startDate,
    endDate,
    activeType,
    updateData,
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

  const getGraphData = () => {
    if (!!activeLines.find((line) => line.displayPrediction)) {
      return [...data, ...tcnData]
    }
    return data
  }

  const xAxisTickFormatter = (date) => {
    return moment(date, 'YYYY-MM-DD hh:mm:ss').format('YYYY-MM-DD')
  }

  return (
    <div className={s.lineGraphWrapper}>
      <LineChart
        width={width}
        height={height}
        data={getGraphData()}
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
        <Tooltip content={<CustomTooltip />} />
        {(activeLines as Array<DataLine>).map((dataLine: DataLine) => {
          const lines = [
            <Line
              key={dataLine.lineId}
              type="monotone"
              dataKey={`${activeType}_${dataLine.lineId}_count`}
              stroke={colors[getColorIndex(dataLine.lineId)]}
              strokeWidth={3}
              dot={false}
            />,
          ]

          if (dataLine.displayTrend) {
            lines.push(
              <Line
                key={`trend_long_${dataLine.lineId}`}
                type="monotone"
                dataKey={`trend_long_${dataLine.lineId}`}
                stroke={'black'}
                strokeWidth={2}
                dot={false}
                strokeDasharray="4"
              />,
              <Line
                key={`trend_short_${dataLine.lineId}`}
                type="monotone"
                dataKey={`trend_short_${dataLine.lineId}`}
                stroke={'black'}
                strokeWidth={2}
                dot={false}
                strokeDasharray="4"
              />,
            )
          }

          if (dataLine.displayPrediction) {
            lines.push(
              <Line
                key={`tcn_pred_${dataLine.lineId}`}
                type="monotone"
                dataKey={`tcn_pred_${dataLine.lineId}`}
                stroke={colors[getColorIndex(dataLine.lineId)] || 'black'}
                strokeWidth={3}
                dot={false}
                strokeDasharray="4"
              />,
            )
          }

          return lines
        })}
      </LineChart>
    </div>
  )
}

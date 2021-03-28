import React from 'react'
import s from './ToolSet.module.scss'
import DatePicker from 'react-datepicker'
import { useContext } from '~contexts'
import { Api, findLastIndex } from '~services'

export const ToolSet = () => {
  const {
    query,
    startDate,
    endDate,
    loading,
    data,
    graphData,
    resolution,
    setResolution,
    setGraphData,
    setData,
    setLoading,
    setQuery,
    setStartDate,
    setEndDate,
  } = useContext()

  const fetchData = React.useCallback(() => {
    setLoading(true)
    Api.linearRegression({
      query: query,
    }).then((res) => {
      console.log(res)
      res['similarWords'] = res['similar_queries']
      setData(res)
      setGraphData(res.dataset.time_series_day)
      setLoading(false)
    })
  }, [query, setData, setLoading])

  React.useEffect(() => {
    if (!data) {
      fetchData()
    }
  }, [data, fetchData])

  React.useEffect(() => {
    if (!data) {
      fetchData()
    } else {
      let graphInterval = getDataInterval()
      if (graphInterval != undefined && graphInterval?.length < 1) {
        alert('Invalid time interval')
      } else {
        console.log(graphInterval)
        console.log(graphInterval)
        setGraphData(graphInterval)
      }
    }
  }, [startDate, endDate, resolution])

  const getDataInterval = () => {
    console.log(startDate.toLocaleDateString())
    let dataset = data?.dataset[`time_series_${resolution}`];
    console.log(`time_series_${resolution}`)
    console.log(dataset)
    let startIndex = dataset.findIndex(
      (d) => d[`time_interval`].split(' ')[0] == startDate.toLocaleDateString(),
    )
    let endIndex = dataset
      .slice()
      .reverse()
      .findIndex((d) => d[`time_interval`].split(' ')[0] == endDate.toLocaleDateString())
    endIndex = endIndex ?? -1;
    endIndex = dataset ? dataset.length - endIndex : endIndex;
    console.log(startIndex)
    console.log(endIndex)
    return dataset.slice(startIndex, endIndex)
  }

  return (
    <>
      {loading ? null : (
        <div className={s.toolSetWrapper}>
          <DatePicker
            onChange={(date: Date) => {
              setStartDate(date)
            }}
            selected={startDate}
          />
          <DatePicker
            onChange={(date: Date) => {
              setEndDate(date)
            }}
            selected={endDate}
          />
          <select onChange={(event) => setResolution(event.target.value.toLocaleLowerCase())}>
            <option value="min">Minute</option>
            <option value="hour">Hour</option>
            <option value="day" defaultChecked>Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value.toLocaleLowerCase())}
          />
          <button onClick={() => fetchData()}>Fetch</button>
        </div>
      )}
    </>
  )
}

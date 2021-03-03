import React from 'react'
import s from './ToolSet.module.scss'
import DatePicker from 'react-datepicker'
import { useContext } from '~contexts'
import { Api } from '~services'

export const ToolSet = () => {
  const {
    query,
    startDate,
    endDate,
    loading,
    data,
    setData,
    setLoading,
    setQuery,
    setStartDate,
    setEndDate,
  } = useContext()

  const fetchData = React.useCallback(() => {
    setLoading(true)
    Api.sarmaRegression({
      query: query,
      start_date: startDate,
      end_date: endDate,
      trunc_by: 'hour',
    }).then((res) => {
      console.log(res)
      setData(res['dataset'])
      setLoading(false)
    })
  }, [startDate, endDate, query, setData, setLoading])

  React.useEffect(() => {
    if (!data.length) {
      fetchData()
    }
  }, [data, fetchData])

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

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

  React.useEffect(() => {
    Api.linearRegression({
      query: query,
      interval_mins: 60 * 24,
      start_date: startDate,
      end_date: endDate,
    }).then((res) => {
      console.log(res)
      setData(res['dataset'])
      setLoading(false)
    })
  }, [startDate, endDate, query, setData])

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
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
      )}
    </>
  )
}

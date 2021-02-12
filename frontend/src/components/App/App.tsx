import React, { useEffect, useState } from 'react'
import DateTimePicker from 'react-datetime-picker'
import s from './App.module.scss'
import { LineGraph } from '~components'
import { Api } from '~services'

export const App = () => {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState([])
  const [query, setQuery] = useState('sommar%')
  const [startDate, setStartDate] = useState(new Date('2021-01-01'))
  const [endDate, setEndDate] = useState(new Date('2021-02-04'))

  useEffect(() => {
    Api.countIntervalIndividual({
      query: query,
      interval_mins: 60 * 24,
      start_date: startDate,
      end_date: endDate,
    }).then((res) => {
      console.log(res)
      setData(res)
      setLoading(false)
    })
  }, [startDate, endDate, query])

  return (
    <div className={s.appWrapper}>
      <header className={s.header}>
        <div>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <>
              <LineGraph
                data={data}
                xLabel={'Time'}
                yLabel={'Count'}
                zLabel={'Query'}
                title={query}
              />
              <DateTimePicker onChange={setStartDate} value={startDate} />
              <DateTimePicker onChange={setEndDate} value={endDate} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} />
            </>
          )}
        </div>
      </header>
    </div>
  )
}

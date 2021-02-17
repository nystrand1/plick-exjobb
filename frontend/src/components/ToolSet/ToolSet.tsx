import React from 'react'
import s from './ToolSet.module.scss'
import DateTimePicker from 'react-datetime-picker'
import { useContext } from '~contexts'

export const ToolSet = () => {
  const { query, startDate, endDate, setQuery, setStartDate, setEndDate } = useContext()
  return (
    <div className={s.toolSetWrapper}>
      <DateTimePicker onChange={setStartDate} value={startDate} />
      <DateTimePicker onChange={setEndDate} value={endDate} />
      <input
        value={query}
        onChange={(event) => setQuery && setQuery(event.target.value)}
      />
    </div>
  )
}

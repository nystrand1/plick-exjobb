import React from 'react'
import s from './ToolSet.module.scss'
import DateTimePicker from 'react-datetime-picker'

interface ToolSetProps {
  query: string
  startDate: Date
  endDate: Date
  setQuery: (query: string) => void
  setStartDate: (date: Date) => void
  setEndDate: (date: Date) => void
}

export const ToolSet = ({
  query,
  startDate,
  endDate,
  setStartDate,
  setEndDate,
  setQuery,
}: ToolSetProps) => {
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

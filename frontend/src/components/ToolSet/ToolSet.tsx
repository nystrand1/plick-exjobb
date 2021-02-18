import React from 'react'
import s from './ToolSet.module.scss'
import DatePicker from 'react-datepicker'
import { useContext } from '~contexts'

export const ToolSet = () => {
  const { query, startDate, endDate, setQuery, setStartDate, setEndDate } = useContext()
  return (
    <div className={s.toolSetWrapper}>
      <DatePicker onChange={(date: Date) => {
        setStartDate(date);
      }} selected={startDate} />
      <DatePicker onChange={(date: Date) => {
        setEndDate(date);
      }} selected={endDate} />
      <input
        value={query}
        onChange={(event) => setQuery && setQuery(event.target.value)}
      />
    </div>
  )
}

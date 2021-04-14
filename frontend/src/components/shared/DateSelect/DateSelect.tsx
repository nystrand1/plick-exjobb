import * as React from 'react'
import s from './DateSelect.module.scss'
import DatePicker from 'react-datepicker'
import { ReactComponent as DownArrow } from '~static/svg/down-arrow.svg'

interface DateSelectProps {
  title: string
  startDate: Date
  onChange: (date: Date) => void
}

export const DateSelect = ({ title, startDate, onChange }: DateSelectProps) => {
  const CustomInput = React.forwardRef(
    ({ value, onClick }: React.ComponentPropsWithRef<'button'>, _) => (
      <button className={s.datePicker} onClick={onClick}>
        {value}
        <DownArrow className={s.downArrow} />
      </button>
    ),
  )

  return (
    <div className={s.dateSelectWrapper}>
      <div className={s.title}>{title}</div>
      <DatePicker
        onChange={(date: Date) => {
          onChange(date)
        }}
        selected={startDate}
        customInput={<CustomInput />}
      />
    </div>
  )
}

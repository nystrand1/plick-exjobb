import * as React from 'react'
import s from './DropDown.module.scss'
import { ReactComponent as DownArrow } from '~static/svg/down-arrow.svg'

interface DropDownProps {
  options: string[]
  onChange: (val: string) => void
  value: string
  title?: string
}

export const DropDown = ({ options, onChange, value, title }: DropDownProps) => {
  return (
    <>
      {options && (
        <div>
          <div className={s.title}>{title}</div>
          <select
            className={s.dateSelect}
            onChange={(e) => onChange(e.target.value)}
            value={value}
          >
            {options?.map((o, i) => (
              <option key={i}>{o}</option>
            ))}
          </select>
          <DownArrow className={s.downArrow} />
        </div>
      )}
    </>
  )
}

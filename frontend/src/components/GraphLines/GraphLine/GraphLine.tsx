import * as React from 'react'
import s from './Line.module.scss'
import { Checkbox } from '@material-ui/core'
import { ReactComponent as ShowMore } from '~static/svg/add.svg'

interface LineProps {
  title: string
  onClick: (id: any) => void
  diff: {
    weekly: number
    monthly: number
  }
  style: any
  id: any
  color: string
}

export const GraphLine = ({ title, onClick, diff, style, id, color }: LineProps) => {
  const [open, setOpen] = React.useState(false)
  const [displayTrendLine, setDisplayTrendLine] = React.useState(false)
  const [displayPrediciton, setDisplayPrediciton] = React.useState(false)

  return (
    <div className={`${s.lineWrapper} ${open ? s.open : ''}`} key={id} style={style}>
      <div className={s.line}>
        <button className={s.button} onClick={() => setOpen(!open)}>
          <ShowMore className={open ? s.open : ''} />
        </button>
        <div className={s.content} onClick={() => onClick(id)}>
          <div className={s.title}>{title}</div>
          <div className={s.values}>
            <div>{diff.weekly} st</div>
            <div>{diff.monthly} st</div>
          </div>
        </div>
      </div>
      <div className={`${s.options} ${open ? s.open : ''}`}>
        <div>
          <Checkbox
            checked={displayTrendLine}
            onChange={(ev) => setDisplayTrendLine(ev.target.checked)}
            style={{ color: color }}
          />
          Visa trendlinje
        </div>
        <div className={s.option}>
          <Checkbox
            checked={displayPrediciton}
            onChange={(ev) => setDisplayPrediciton(ev.target.checked)}
            style={{ color: color }}
          />
          Visa prediction
        </div>
      </div>
    </div>
  )
}

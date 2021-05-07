import * as React from 'react'
import s from './Line.module.scss'
import { Checkbox, IconButton } from '@material-ui/core'
import { ReactComponent as ShowMore } from '~static/svg/add.svg'

interface LineProps {
  title: string
  onClick: (newLine: DataLine, toggle?: boolean) => void
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

  const toggleTrend = (checked: boolean) => {
    setDisplayTrendLine(checked)
    onClick(
      {
        lineId: id,
        displayPrediction: displayPrediciton,
        displayTrend: checked,
      },
      false,
    )
  }

  const togglePred = (checked: boolean) => {
    setDisplayPrediciton(checked)
    onClick(
      {
        lineId: id,
        displayPrediction: checked,
        displayTrend: displayTrendLine,
      },
      false,
    )
  }

  return (
    <div className={`${s.lineWrapper} ${open ? s.open : ''}`} key={id} style={style}>
      <div className={s.line}>
        <IconButton className={s.button} onClick={() => setOpen(!open)}>
          <ShowMore className={open ? s.open : ''} />
        </IconButton>
        <div
          className={s.content}
          onClick={() =>
            onClick(
              {
                lineId: id,
                displayPrediction: displayPrediciton,
                displayTrend: displayTrendLine,
              },
              true,
            )
          }
        >
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
            onChange={(ev) => toggleTrend(ev.target.checked)}
            style={{ color: color }}
          />
          Visa trendlinjer
        </div>
        <div className={s.option}>
          <Checkbox
            checked={displayPrediciton}
            onChange={(ev) => togglePred(ev.target.checked)}
            style={{ color: color }}
          />
          Visa prediction
        </div>
      </div>
    </div>
  )
}

import * as React from 'react'
import s from '../GraphLines.module.scss'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { ReactComponent as DownArrow } from '~static/svg/down-arrow.svg'

interface QueryLinesProps {
  onClick: (line: any) => void
}

export const QueryLines = ({ onClick }: QueryLinesProps) => {
  const { topListQueries, activeQueries } = useContext()
  return (
    <>
      {topListQueries?.map((line, i) => {
        const style = activeQueries.includes(line.query)
          ? { borderColor: colors[i % colors.length] }
          : {}
        return (
          <div className={s.line} style={style} key={line.query}>
            <button className={s.button} onClick={() => console.log('open')}>
              <DownArrow />
            </button>
            <div className={s.content} onClick={() => onClick(line)}>
              <div className={s.title}>{line.query}</div>
              <div className={s.values}>
                <div>{line.weekly_diff}</div>
                <div>{line.monthly_diff}</div>
              </div>
            </div>
          </div>
        )
      })}
    </>
  )
}

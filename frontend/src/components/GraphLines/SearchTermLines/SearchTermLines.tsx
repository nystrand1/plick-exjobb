import * as React from 'react'
import s from '../GraphLines.module.scss'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { ReactComponent as DownArrow } from '~static/svg/down-arrow.svg'
import { ReactComponent as MoreIcon } from '~static/svg/more.svg'

interface SearchTermLinesProps {
  onClick: (line: any) => void
}

export const SearchTermLines = ({ onClick }: SearchTermLinesProps) => {
  const { topListSearchTerms, activeLines } = useContext()
  return (
    <>
      {topListSearchTerms?.map((line, i) => {
        const style = activeLines.includes(i)
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

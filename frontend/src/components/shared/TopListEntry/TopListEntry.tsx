import * as React from 'react'
import s from './TopListEntry.module.scss'
import { ReactComponent as ShowMore } from '~static/svg/more.svg'

interface TopListEntryProps {
  query: string
  metric: number
  index: number
  image?: string
  words?: string[]
}

export const TopListEntry = ({
  query,
  metric,
  index,
  image,
  words,
}: TopListEntryProps) => {
  return (
    <div className={s.entryWrapper}>
      <div className={s.text}>
        <h3 className={s.index}>{index}</h3>
        <div className={s.queryWrapper}>
          <div className={s.query}>{query}</div>
          <div className={s.metric}>+{metric}%</div>
          {words?.length && <div className={s.words}>{words.join(', ')}</div>}
        </div>
      </div>
      <div className={s.imageWrapper}>
        <img src={image} alt={query} className={s.image} />
        <button className={s.showMore}>
          <ShowMore />
        </button>
      </div>
    </div>
  )
}

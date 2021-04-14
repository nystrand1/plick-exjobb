import * as React from 'react'
import s from './GraphLines.module.scss'
import { colors } from '~utils'
import { ReactComponent as DownArrow } from '~static/svg/down-arrow.svg'
import { ReactComponent as SearchIcon } from '~static/svg/search.svg'
import { ReactComponent as MoreIcon } from '~static/svg/more.svg'

export const GraphLines = () => {
  const [activeLines, setActiveLines] = React.useState([1, 2])
  const lines = [
    {
      id: 0,
      query: 'Skor',
      metrics: [
        {
          longTerm: 2,
          shortTerm: 14,
        },
      ],
      words: ['Nike', 'Skor 38', 'Air Force 1', 'Adidas'],
    },
    {
      id: 1,
      query: 'Tröjor',
      metrics: [
        {
          longTerm: 2,
          shortTerm: 14,
        },
      ],
    },
    {
      id: 2,
      query: 'Byxor',
      metrics: [
        {
          longTerm: 2,
          shortTerm: 14,
        },
      ],
    },
    {
      id: 3,
      query: 'Mössor',
      metrics: [
        {
          longTerm: 2,
          shortTerm: 14,
        },
      ],
    },
  ]

  const toggleLine = (line) => {
    const i = activeLines.indexOf(line.id)
    if (i === -1) {
      setActiveLines([...activeLines, line.id])
    } else {
      const tmpArr = [...activeLines]
      tmpArr.splice(i, 1)
      setActiveLines(tmpArr)
    }
  }

  return (
    <div className={s.graphLinesWrapper}>
      <div className={s.search}>
        <SearchIcon className={s.icon} />
        <input placeholder={'Lägg till kategori'} />
      </div>
      <div className={s.linesTitle}>
        <div>KATEGORI</div>
        <div className={s.metricsTitle}>
          <div>KORT INTERVALL</div>
          <div>LÅNGT INTERVALL</div>
        </div>
      </div>
      {lines.map((line) => {
        const style = activeLines.includes(line.id)
          ? { borderColor: colors[line.id % colors.length] }
          : {}
        return (
          <div className={s.line} style={style} key={line.id}>
            <button className={s.button} onClick={() => console.log('open')}>
              <DownArrow />
            </button>
            <div className={s.content} onClick={() => toggleLine(line)}>
              <div className={s.title}>{line.query}</div>
              <div className={s.values}>
                {line.metrics?.map((metric, i) => (
                  <React.Fragment key={i}>
                    <div>{metric.longTerm}</div>
                    <div>{metric.shortTerm}</div>
                  </React.Fragment>
                ))}
              </div>
            </div>
            <button className={s.button} onClick={() => console.log('more')}>
              <MoreIcon />
            </button>
          </div>
        )
      })}
    </div>
  )
}

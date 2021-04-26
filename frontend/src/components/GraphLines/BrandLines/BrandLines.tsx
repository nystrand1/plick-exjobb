import * as React from 'react'
import s from '../GraphLines.module.scss'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { ReactComponent as ShowMore } from '~static/svg/add.svg'

interface BrandLinesProps {
  onClick: (line: any) => void
}

export const BrandLines = ({ onClick }: BrandLinesProps) => {
  const { topListBrands, activeBrands } = useContext()
  return (
    <>
      {topListBrands?.map((line, i) => {
        const style = activeBrands.includes(line.brand_id)
          ? { borderColor: colors[i % colors.length] }
          : {}
        return (
          <div className={s.line} style={style} key={line.brand_id}>
            <button className={s.button} onClick={() => console.log('open')}>
              <ShowMore />
            </button>
            <div className={s.content} onClick={() => onClick(line)}>
              <div className={s.title}>{line.brand_name}</div>
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

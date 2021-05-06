import * as React from 'react'
import s from './GraphLines.module.scss'
import { useContext } from '~contexts'
import { ReactComponent as SearchIcon } from '~static/svg/search.svg'
import { QueryLines } from './QueryLines'
import { BrandLines } from './BrandLines'
import { CategoryLines } from './CategoryLines'

export const GraphLines = () => {
  const {
    activeLines,
    setActiveBrands,
    setActiveCategories,
    setActiveQueries,
    activeType,
  } = useContext()

  const setActiveLines = (lines) => {
    switch (activeType) {
      case 'brand':
        setActiveBrands(lines)
        break
      case 'category':
        setActiveCategories(lines)
        break
      case 'query':
      default:
        setActiveQueries(lines)
    }
  }

  const toggleLine = (newLine: DataLine, toggle = false) => {
    const index = activeLines.findIndex(
      (activeLine) => activeLine.lineId === newLine.lineId,
    )
    if (index === -1) {
      setActiveLines([...activeLines, newLine])
    } else {
      const tmpArr = [...activeLines]
      if (toggle) {
        tmpArr.splice(index, 1)
      } else {
        tmpArr[index] = newLine
      }
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
      {activeType === 'query' && <QueryLines onClick={toggleLine} />}
      {activeType === 'brand' && <BrandLines onClick={toggleLine} />}
      {activeType === 'category' && <CategoryLines onClick={toggleLine} />}
    </div>
  )
}

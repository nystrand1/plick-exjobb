import * as React from 'react'
import s from './GraphLines.module.scss'
import { useContext } from '~contexts'
import { ReactComponent as SearchIcon } from '~static/svg/search.svg'
import { SearchTermLines } from './SearchTermLines'
import { BrandLines } from './BrandLines'
import { CategoryLines } from './CategoryLines'

export const GraphLines = () => {
  const { activeType, activeLines, setActiveLines } = useContext()

  const toggleLine = (line) => {
    let id

    switch (activeType) {
      case 'searchTerms':
        id = line.query
        break
      case 'brands':
        id = line.brand_name
        break
      case 'categories':
        id = line.category_name
        break
    }

    const i = activeLines.indexOf(id)
    if (i === -1) {
      setActiveLines([...activeLines, id])
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
      {activeType === 'searchTerms' && <SearchTermLines onClick={toggleLine} />}
      {activeType === 'brands' && <BrandLines onClick={toggleLine} />}
      {activeType === 'categories' && <CategoryLines onClick={toggleLine} />}
    </div>
  )
}

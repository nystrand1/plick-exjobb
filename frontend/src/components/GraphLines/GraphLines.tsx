import * as React from 'react'
import s from './GraphLines.module.scss'
import { useContext } from '~contexts'
import { ReactComponent as SearchIcon } from '~static/svg/search.svg'
import { QueryLines } from './QueryLines'
import { BrandLines } from './BrandLines'
import { CategoryLines } from './CategoryLines'

export const GraphLines = () => {
  const {
    activeType,
    activeBrands,
    activeCategories,
    activeQueries,
    setActiveBrands,
    setActiveCategories,
    setActiveQueries,
  } = useContext()

  const toggleLine = (line) => {
    let id

    switch (activeType) {
      case 'query':
        id = line.query
        const queryIndex = activeQueries.indexOf(id)
        if (queryIndex === -1) {
          setActiveQueries([...activeQueries, id])
        } else {
          const tmpArr = [...activeQueries]
          tmpArr.splice(queryIndex, 1)
          setActiveQueries(tmpArr)
        }
        break
      case 'brand':
        id = line.brand_id
        const brandIndex = activeBrands.indexOf(id)
        if (brandIndex === -1) {
          setActiveBrands([...activeBrands, id])
        } else {
          const tmpArr = [...activeBrands]
          tmpArr.splice(brandIndex, 1)
          setActiveBrands(tmpArr)
        }
        break
      case 'category':
        id = line.category_id
        const categoryIndex = activeCategories.indexOf(id)
        if (categoryIndex === -1) {
          setActiveCategories([...activeCategories, id])
        } else {
          const tmpArr = [...activeCategories]
          tmpArr.splice(categoryIndex, 1)
          setActiveCategories(tmpArr)
        }
        break
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

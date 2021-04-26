import * as React from 'react'
import s from './Dashboard.module.scss'
import { Api } from '~services'
import { TopList, GraphTool } from '~components'
import { useContext } from '~contexts'

export const Dashboard = () => {
  const {
    setTopListQueries,
    setTopListBrands,
    setTopListCategories,
    setActiveQueries,
    setActiveBrands,
    setActiveCategories,
  } = useContext()
  React.useEffect(() => {
    Api.trendingQueries({ limit: 5 }).then((data) => {
      setTopListQueries(data)
      setActiveQueries([data[0].query])
    })
    Api.trendingBrands({ limit: 5 }).then((data) => {
      setTopListBrands(data)
      setActiveBrands([data[0].brand_id])
    })
    Api.trendingCategories({ limit: 5 }).then((data) => {
      setTopListCategories(data)
      setActiveCategories([data[0].category_id])
    })
  }, [
    setTopListQueries,
    setTopListBrands,
    setTopListCategories,
    setActiveBrands,
    setActiveQueries,
    setActiveCategories,
  ])
  return (
    <div className={`${s.dashboardWrapper}`}>
      <div className="row">
        <TopList type="searchTerms" />
        <TopList type="brands" />
        <TopList type="categories" />
      </div>
      <div className="row">
        <GraphTool />
      </div>
    </div>
  )
}

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
      setActiveQueries([
        { lineId: data[0].query, displayPrediction: false, displayTrend: false },
      ])
    })
    Api.trendingBrands({ limit: 5 }).then((data) => {
      setTopListBrands(data)
      setActiveBrands([
        { lineId: data[0].brand_id, displayPrediction: false, displayTrend: false },
      ])
    })
    Api.trendingCategories({ limit: 5 }).then((data) => {
      setTopListCategories(data)
      setActiveCategories([
        { lineId: data[0].category_id, displayPrediction: false, displayTrend: false },
      ])
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

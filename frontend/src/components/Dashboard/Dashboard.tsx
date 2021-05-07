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
    queriesTime,
    brandsTime,
    categoriesTime,
  } = useContext()

  React.useEffect(() => {
    Api.trendingQueries({ limit: 5, future: queriesTime === 'nästa vecka'}).then((data) => {
      setTopListQueries(data)
      setActiveQueries([
        { lineId: data[0].query, displayPrediction: false, displayTrend: false },
      ])
    })
  }, [setTopListQueries, setActiveQueries, queriesTime])

  React.useEffect(() => {
    Api.trendingBrands({ limit: 5, future: brandsTime === 'nästa vecka' }).then((data) => {
      setTopListBrands(data)
      setActiveBrands([
        { lineId: data[0].brand_id, displayPrediction: false, displayTrend: false },
      ])
    })
  }, [setTopListBrands, setActiveBrands, brandsTime])

  React.useEffect(() => {
    Api.trendingCategories({ limit: 5, future: categoriesTime === 'nästa vecka' }).then((data) => {
      setTopListCategories(data)
      setActiveCategories([
        { lineId: data[0].category_id, displayPrediction: false, displayTrend: false },
      ])
    })
  }, [setTopListCategories, setActiveCategories, categoriesTime])
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

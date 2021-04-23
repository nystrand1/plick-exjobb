import * as React from 'react'
import s from './Dashboard.module.scss'
import { Api } from '~services'
import { TopList, GraphTool } from '~components'
import { useContext } from '~contexts'

export const Dashboard = () => {
  const { setTopListQueries, setTopListBrands, setTopListCategories } = useContext()
  React.useEffect(() => {
    Api.trendingQueries({ limit: 5 }).then((data) => {
      setTopListQueries(data)
    })
    Api.trendingBrands({ limit: 5 }).then((data) => {
      setTopListBrands(data)
    })
    Api.trendingCategories({ limit: 5 }).then((data) => {
      setTopListCategories(data)
    })
  }, [setTopListQueries, setTopListBrands, setTopListCategories])
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

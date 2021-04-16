import * as React from 'react'
import s from './Dashboard.module.scss'
import { Api } from '~services'
import { TopList, GraphTool } from '~components'
import { useContext } from '~contexts'

export const Dashboard = () => {
  const { setTopListSearchTerms, setTopListBrands, setTopListCategories } = useContext()
  React.useEffect(() => {
    Api.trendingSearchTerms({ limit: 5 }).then((data) => {
      setTopListSearchTerms(data)
    })
    Api.trendingBrands({ limit: 5 }).then((data) => {
      setTopListBrands(data)
    })
    Api.trendingCategories({ limit: 5 }).then((data) => {
      setTopListCategories(data)
    })
  }, [setTopListSearchTerms, setTopListBrands, setTopListCategories])
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

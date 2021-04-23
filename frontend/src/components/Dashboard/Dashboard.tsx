import * as React from 'react'
import s from './Dashboard.module.scss'
import { Api } from '~services'
import { TopList, GraphTool } from '~components'
import { useContext } from '~contexts'

export const Dashboard = () => {
  const {
    setTopListSearchTerms,
    setTopListBrands,
    setTopListCategories,
    setTimeSeriesSerachTerms,
  } = useContext()
  React.useEffect(() => {
    Api.trendingSearchTerms({ limit: 5 }).then((data) => {
      setTopListSearchTerms(data)

      const tmpArr: ITimeSeriesSearchTerms[] = []
      data.forEach((element) => {
        Api.queryDataset({ query: element.query }).then((data) => {
          tmpArr.push(data[0])
        })
      })
      setTimeSeriesSerachTerms(tmpArr)
    })
    Api.trendingBrands({ limit: 5 }).then((data) => {
      setTopListBrands(data)
    })
    Api.trendingCategories({ limit: 5 }).then((data) => {
      setTopListCategories(data)
    })
  }, [
    setTopListSearchTerms,
    setTopListBrands,
    setTopListCategories,
    setTimeSeriesSerachTerms,
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

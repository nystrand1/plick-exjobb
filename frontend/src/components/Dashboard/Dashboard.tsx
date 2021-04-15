import * as React from 'react'
import s from './Dashboard.module.scss'
import { Api } from '~services'
import { TopList, GraphTool } from '~components'
import { useContext } from '~contexts'

export const Dashboard = () => {
  const [data, setData] = React.useState(null)
  React.useEffect(() => {
    Api.trendingWords({ limit: 10 }).then((data) => {
      setData(data)
      console.log(data)
    })
  }, [])
  if (!data) {
    return 'LOADING...'
  }
  return (
    <div className={`${s.dashboardWrapper}`}>
      <div className="row">
        <TopList type="queries" />
        <TopList type="brands" />
        <TopList type="categories" />
      </div>
      <div className="row">
        <GraphTool />
      </div>
    </div>
  )
}

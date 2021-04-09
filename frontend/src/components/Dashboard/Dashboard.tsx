import * as React from 'react'
import s from './Dashboard.module.scss'
import { TopList, GraphTool } from '~components'

export const Dashboard = () => {
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

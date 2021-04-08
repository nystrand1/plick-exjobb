import * as React from 'react'
import s from './Dashboard.module.scss'
import { TopList, GraphTool } from '~components'

export const Dashboard = () => {
  return (
    <div className={`${s.dashboardWrapper}`}>
      <div className="row">
        <TopList type="Queries" />
        <TopList type="Brands" />
        <TopList type="Categories" />
      </div>
      <div className="row">
        <GraphTool />
      </div>
    </div>
  )
}

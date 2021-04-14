import s from './App.module.scss'
import { Route } from 'react-router-dom'
import { Test, Dashboard, Navbar } from '~components'

export const App = () => {
  return (
    <div className={s.appWrapper}>
      <Navbar />
      <div className={s.contentWrapper}>
        <Route path={'/test'} component={Test} />
        <Route path={'/'} component={Dashboard} />
      </div>
    </div>
  )
}

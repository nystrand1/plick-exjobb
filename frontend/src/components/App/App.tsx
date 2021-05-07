import s from './App.module.scss'
import { Route } from 'react-router-dom'
import { Test, Dashboard, Navbar, Modal } from '~components'

export const App = () => {
  return (
    <div className={s.appWrapper}>
      <Modal />
      <Navbar />
      <div className={s.contentWrapper}>
        <Route path={'/test'} component={Test} />
        <Route path={'/'} component={Dashboard} />
      </div>
    </div>
  )
}

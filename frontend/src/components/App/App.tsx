import s from './App.module.scss'
import { Route } from 'react-router-dom'
import { Test } from '~components'

export const App = () => {
  return (
    <div className={s.appWrapper}>
      <Route path={'/test'} component={Test} />
      <Route path={'/'} render={() => <div>hello</div>} />
    </div>
  )
}

import React from 'react'
import ReactDOM from 'react-dom'
import '~styles/global.scss'
import { App } from '~components'

const Root = (
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

ReactDOM.render(Root, document.getElementById('root'))

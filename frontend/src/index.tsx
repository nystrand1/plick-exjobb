import React from 'react'
import ReactDOM from 'react-dom'
import '~styles/global.scss'
import { App } from '~components'
import { Provider } from '~contexts'

const Root = (
  <React.StrictMode>
    <Provider>
      <App />
    </Provider>
  </React.StrictMode>
)

ReactDOM.render(Root, document.getElementById('root'))

import React from 'react'
import ReactDOM from 'react-dom'
import '~styles/global.scss'
import { App } from '~components'
import { Provider } from '~contexts'
import { BrowserRouter as Router } from 'react-router-dom'

const Root = (
  <React.StrictMode>
    <Provider>
      <Router>
        <App />
      </Router>
    </Provider>
  </React.StrictMode>
)

ReactDOM.render(Root, document.getElementById('root'))

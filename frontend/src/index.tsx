import React from 'react'
import ReactDOM from 'react-dom'
import { BrowserRouter as Router } from 'react-router-dom'
import 'typeface-open-sans'
import 'bootstrap/dist/css/bootstrap.css'
import '~styles/global.scss'
import { App } from '~components'
import { Provider } from '~contexts'

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

import * as React from 'react'
import s from './App.module.scss'
import { LineGraph } from '~components'
import { ToolSet } from '~components/ToolSet'
import { useContext } from '~contexts'

export const App = () => {
  const { query, loading, data } = useContext()

  return (
    <div className={s.appWrapper}>
      <header className={s.header}>
        <div>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <>
              <LineGraph
                data={data}
                xLabel={'Time'}
                yLabel={'Count'}
                zLabel={'Query'}
                title={query}
              />
            </>
          )}
          <ToolSet />
        </div>
      </header>
    </div>
  )
}

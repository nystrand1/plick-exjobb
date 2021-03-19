import * as React from 'react'
import s from './App.module.scss'
import { LineGraph, ToolSet, SimilarWords } from '~components'

import { useContext } from '~contexts'


export const App = () => {
  const { query, loading, data } = useContext();
  React.useEffect(() => {
    console.log(data);
  }, [loading]);
  return (
    <div className={s.appWrapper}>
      <header className={s.header}>
        <div>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <>
              <LineGraph
                data={data?.dataset}
                xLabel={'Time'}
                yLabel={'Count'}
                zLabel={'Query'}
                title={query}
              />
              {!!data?.similarWords?.length && (
                <SimilarWords words={data?.similarWords}/>
              )}
            </>
          )}
          <ToolSet />
        </div>
      </header>
    </div>
  )
}

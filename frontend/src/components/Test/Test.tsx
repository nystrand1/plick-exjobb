import * as React from 'react'
import s from './Test.module.scss'
import { LineGraph, ToolSet, SimilarWords } from '~components'
import { useContext } from '~contexts'

export const Test = () => {
  const { query, loading, data, graphData } = useContext()
  React.useEffect(() => {
    console.log(graphData)
  }, [loading, data, graphData])

  return (
    <header className={s.header}>
      <div>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
            <LineGraph
              data={graphData}
              xLabel={'Time'}
              yLabel={'Count'}
              zLabel={'Query'}
              title={query}
            />
            {!!data?.similarWords?.length && <SimilarWords words={data?.similarWords} />}
          </>
        )}
        <ToolSet />
      </div>
    </header>
  )
}

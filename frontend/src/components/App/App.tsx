import * as React from 'react'
import s from './App.module.scss'
import { LineGraph } from '~components'
import { Api } from '~services'
import { ToolSet } from '~components/ToolSet'
import { useContext } from '~contexts'

export const App = () => {
  const [loading, setLoading] = React.useState(true)
  const { data, query, startDate, endDate, setData } = useContext()

  React.useEffect(() => {
    Api.linearRegression({
      query: query,
      interval_mins: 60,
      start_date: startDate,
      end_date: endDate,
    }).then((res) => {
      console.log(res)
      setData(res)
      setLoading(false)
    })
  }, [startDate, endDate, query, setData])

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
              <ToolSet />
            </>
          )}
        </div>
      </header>
    </div>
  )
}

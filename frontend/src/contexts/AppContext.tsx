import * as React from 'react'

const useProviderValue = () => {
  const [data, setData] = React.useState<IData>()
  const [query, setQuery] = React.useState('nike')
  const [startDate, setStartDate] = React.useState(new Date('2021-01-01'))
  const [endDate, setEndDate] = React.useState(new Date('2021-02-18'))
  const [loading, setLoading] = React.useState(true)
  const [graphData, setGraphData] = React.useState<IDataSet[]>()
  const [resolution, setResolution] = React.useState('dag')

  const value = React.useMemo(
    () => ({
      data,
      query,
      startDate,
      endDate,
      loading,
      graphData,
      resolution,
      setResolution,
      setGraphData,
      setLoading,
      setData,
      setQuery,
      setStartDate,
      setEndDate,
    }),
    [
      data,
      query,
      startDate,
      endDate,
      loading,
      graphData,
      resolution,
      setResolution,
      setGraphData,
      setData,
      setQuery,
      setStartDate,
      setEndDate,
      setLoading,
    ],
  )
  return value
}

type IContext = ReturnType<typeof useProviderValue>
const Context = React.createContext<IContext | undefined>(undefined)

export const Provider: React.FC = (props) => {
  const value = useProviderValue()
  return <Context.Provider value={value} {...props} />
}

export const useContext = () => {
  const context = React.useContext(Context)
  if (context === undefined) {
    throw new Error(`useContext must be used within a Provider`)
  }
  return context
}

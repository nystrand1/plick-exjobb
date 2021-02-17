import * as React from 'react'

const useProviderValue = () => {
  const [data, setData] = React.useState<Data[]>([])
  const [query, setQuery] = React.useState('nike')
  const [startDate, setStartDate] = React.useState(new Date('2020-12-30'))
  const [endDate, setEndDate] = React.useState(new Date('2020-12-31'))

  const value = React.useMemo(
    () => ({
      data,
      query,
      startDate,
      endDate,
      setData,
      setQuery,
      setStartDate,
      setEndDate,
    }),
    [data, query, startDate, endDate, setData, setQuery, setStartDate, setEndDate],
  )
  return value
}
export type IContext = ReturnType<typeof useProviderValue>

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

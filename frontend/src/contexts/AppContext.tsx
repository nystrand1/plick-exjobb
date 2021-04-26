import * as React from 'react'

const useProviderValue = () => {
  const [data, setData] = React.useState<IData>()
  const [query, setQuery] = React.useState('nike')
  const [graphData, setGraphData] = React.useState<IDataSet[]>()
  const [loading, setLoading] = React.useState(true)

  const [topListQueries, setTopListQueries] = React.useState<ITopListSearchTerm[]>()
  const [topListBrands, setTopListBrands] = React.useState<ITopListBrand[]>()
  const [topListCategories, setTopListCategories] = React.useState<ITopListCategory[]>()

  const [startDate, setStartDate] = React.useState(new Date('2021-01-01 00:00:00'))
  const [endDate, setEndDate] = React.useState(new Date())
  const [resolution, setResolution] = React.useState('week')

  const [activeBrands, setActiveBrands] = React.useState<number[]>([])
  const [activeCategories, setActiveCategories] = React.useState<number[]>([])
  const [activeQueries, setActiveQueries] = React.useState<string[]>([])

  const [activeType, setactiveType] = React.useState<'query' | 'brand' | 'category'>(
    'query',
  )

  const value = React.useMemo(
    () => ({
      data,
      topListQueries,
      topListBrands,
      topListCategories,
      query,
      startDate,
      endDate,
      graphData,
      resolution,
      loading,
      activeBrands,
      activeCategories,
      activeQueries,
      activeType,
      setData,
      setTopListQueries,
      setTopListBrands,
      setTopListCategories,
      setQuery,
      setStartDate,
      setEndDate,
      setGraphData,
      setResolution,
      setLoading,
      setActiveBrands,
      setActiveCategories,
      setActiveQueries,
      setactiveType,
    }),
    [
      data,
      topListQueries,
      topListBrands,
      topListCategories,
      query,
      startDate,
      endDate,
      loading,
      graphData,
      resolution,
      activeBrands,
      activeCategories,
      activeQueries,
      activeType,
      setData,
      setTopListQueries,
      setTopListBrands,
      setTopListCategories,
      setQuery,
      setEndDate,
      setStartDate,
      setGraphData,
      setResolution,
      setLoading,
      setActiveBrands,
      setActiveCategories,
      setActiveQueries,
      setactiveType,
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

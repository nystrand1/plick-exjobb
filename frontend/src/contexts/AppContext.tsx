import * as React from 'react'

const useProviderValue = () => {
  const [data, setData] = React.useState<IData>()
  const [query, setQuery] = React.useState('nike')
  const [graphData, setGraphData] = React.useState<IDataSet[]>()
  const [loading, setLoading] = React.useState(true)

  const [topListQueries, setTopListQueries] = React.useState<ITopListSearchTerm[]>()
  const [topListBrands, setTopListBrands] = React.useState<ITopListBrand[]>()
  const [topListCategories, setTopListCategories] = React.useState<ITopListCategory[]>()
  const [queriesTime, setQueriesTime] = React.useState('1 vecka')
  const [brandsTime, setBrandsTime] = React.useState('1 vecka')
  const [categoriesTime, setCategoriesTime] = React.useState('1 vecka')

  const [startDate, setStartDate] = React.useState(new Date('2021-01-01 00:00:00'))
  const [endDate, setEndDate] = React.useState(new Date())
  const [resolution, setResolution] = React.useState('day')

  const [activeBrands, setActiveBrands] = React.useState<DataLine[]>([])
  const [activeCategories, setActiveCategories] = React.useState<DataLine[]>([])
  const [activeQueries, setActiveQueries] = React.useState<DataLine[]>([])

  const [activeType, setactiveType] = React.useState<'query' | 'brand' | 'category'>(
    'query',
  )

  const [modalEntry, setModalEntry] = React.useState<string | null>(null)
  const [exampleAds, setExampleAds] = React.useState<any[]>([])

  const activeLines = React.useMemo(() => {
    switch (activeType) {
      case 'brand':
        return activeBrands
      case 'category':
        return activeCategories
      case 'query':
      default:
        return activeQueries
    }
  }, [activeBrands, activeCategories, activeQueries, activeType])

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
      activeLines,
      exampleAds,
      modalEntry,
      queriesTime,
      categoriesTime,
      brandsTime,
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
      setExampleAds,
      setModalEntry,
      setQueriesTime,
      setCategoriesTime,
      setBrandsTime
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
      activeLines,
      exampleAds,
      modalEntry,
      queriesTime,
      categoriesTime,
      brandsTime,
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
      setExampleAds,
      setModalEntry,
      setQueriesTime,
      setCategoriesTime,
      setBrandsTime
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

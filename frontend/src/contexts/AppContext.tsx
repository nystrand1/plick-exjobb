import * as React from 'react'

const useProviderValue = () => {
  const [data, setData] = React.useState<IData>()
  const [topListSearchTerms, setTopListSearchTerms] = React.useState<
    ITopListSearchTerm[]
  >()
  const [topListBrands, setTopListBrands] = React.useState<ITopListBrand[]>()
  const [topListCategories, setTopListCategories] = React.useState<ITopListCategory[]>()
  const [query, setQuery] = React.useState('nike')
  const [startDate, setStartDate] = React.useState(new Date('2021-01-01'))
  const [endDate, setEndDate] = React.useState(new Date('2021-02-18'))
  const [graphData, setGraphData] = React.useState<IDataSet[]>()
  const [resolution, setResolution] = React.useState('dag')
  const [loading, setLoading] = React.useState(true)
  const [activeLines, setActiveLines] = React.useState<number[]>([])
  const [activeType, setactiveType] = React.useState<
    'searchTerms' | 'brands' | 'categories'
  >('brands')

  const value = React.useMemo(
    () => ({
      data,
      topListSearchTerms,
      topListBrands,
      topListCategories,
      query,
      startDate,
      endDate,
      graphData,
      resolution,
      loading,
      activeLines,
      activeType,
      setData,
      setTopListSearchTerms,
      setTopListBrands,
      setTopListCategories,
      setQuery,
      setStartDate,
      setEndDate,
      setGraphData,
      setResolution,
      setLoading,
      setActiveLines,
      setactiveType,
    }),
    [
      data,
      topListSearchTerms,
      topListBrands,
      topListCategories,
      query,
      startDate,
      endDate,
      loading,
      graphData,
      resolution,
      activeLines,
      activeType,
      setData,
      setTopListSearchTerms,
      setTopListBrands,
      setTopListCategories,
      setQuery,
      setEndDate,
      setStartDate,
      setGraphData,
      setResolution,
      setLoading,
      setActiveLines,
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

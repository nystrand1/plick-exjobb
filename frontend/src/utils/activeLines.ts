import { useContext } from '~contexts'

export const getActiveLines = () => {
  const { activeType, activeBrands, activeCategories, activeQueries } = useContext()
  switch (activeType) {
    case 'brand':
      return activeBrands
    case 'category':
      return activeCategories
    case 'query':
    default:
      return activeQueries
  }
}

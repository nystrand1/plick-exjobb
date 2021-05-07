import { useContext } from '~contexts'
import s from './CustomToolTip.module.scss'

export const CustomTooltip = (props) => {
  const { payload, active, label, tickFormatter } = props
  const { topListBrands, topListCategories, activeType } = useContext();


  const getTopicName = (payload) => {
    switch (activeType) {
      case 'brand':
        const brandId = parseInt(payload.name.replace('brand_', '').replace('_count', ''))
        return topListBrands?.find((element) => element.brand_id === brandId)?.brand_name
      case 'category':
        const categoryId = parseInt(payload.name.replace('category_', '').replace('_count', ''))
        return topListCategories?.find((element) => element.category_id === categoryId)?.category_name
      case 'query':
        return payload.name
        .replace('query_', '')
        .replace('_count', '')
        .replace('_long_', ' long ')
        .replace('_short_', ' kort ')
      default:
        return 0
    }
  }

  if (active) {
    const formattedLabel = label?.slice(0, 10)
    return (
      <div className={s.tooltipWrapper}>
        <div className={s.date}>
          {tickFormatter ? tickFormatter(formattedLabel) : formattedLabel}
        </div>
        {payload &&
          payload.length > 0 &&
          payload.map((p, i) => {
            return (
            <div className={s.data} key={i}>
              <div className={s.name}>
                {getTopicName(p)}
              </div>
              <div className={s.value}>
                <div className={s.val}>{Math.round(p.value)}</div> sökningar
              </div>
            </div>
          )})}
      </div>
    )
  }

  return null
}

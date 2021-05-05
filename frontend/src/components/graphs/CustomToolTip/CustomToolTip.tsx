import s from './CustomToolTip.module.scss'

export const CustomTooltip = (props) => {
  const { payload, active, label, tickFormatter } = props
  console.log(payload)
  if (active) {
    const formattedLabel = label.slice(0, 10)
    return (
      <div className={s.tooltipWrapper}>
        <div className={s.date}>
          {tickFormatter ? tickFormatter(formattedLabel) : formattedLabel}
        </div>
        {payload &&
          payload.length > 0 &&
          payload.map((p) => (
            <div className={s.data}>
              <div className={s.name}>
                {p.name.replace('query_', '').replace('_count', '')}
              </div>
              <div className={s.value}>
                <div className={s.val}>{p.value}</div> sökningar
              </div>
            </div>
          ))}
      </div>
    )
  }

  return null
}

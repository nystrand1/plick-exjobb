import s from './CustomToolTip.module.scss'

export const CustomTooltip = (props) => {
  const { payload, active, label, tickFormatter } = props
  if (active) {
    return (
      <div className={s.tooltipWrapper}>
        <div className="label">{tickFormatter ? tickFormatter(label) : label}</div>
        <div className="intro">Count: {payload ? payload[0].value : '0'}</div>
      </div>
    )
  }

  return null
}

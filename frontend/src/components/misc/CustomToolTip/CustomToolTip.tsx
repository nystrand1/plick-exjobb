import s from './CustomToolTip.module.scss'

export const CustomTooltip = (props: any) => {
  const { payload, active, label, fallBackName } = props
  const data = payload && payload[0] ? payload[0].payload : false
  if (active) {
    return (
      <div className={s.customTooltip}>
        <p className="label">{label}</p>
        <p className="intro">Count: {payload ? payload[0].value : '0'}</p>
        <p className="desc">{data?.query ?? fallBackName}</p>
      </div>
    )
  }

  return null
}

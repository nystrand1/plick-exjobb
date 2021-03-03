import s from './CustomToolTip.module.scss'

export const CustomTooltip = (props: any) => {
  const { payload, active, label, fallBackName } = props
  const data = payload && payload[0] ? payload[0].payload : false
  if (active) {
    return (
      <div className={s.customTooltip}>
        <p className="label">{label}</p>
        {payload?.map((graph => {
          return <>
            <p key={graph.dataKey} className="intro">{graph.name}: {Math.round(graph.value)}</p>
          </>
        }))}
        <p className="desc">{data?.query ?? fallBackName}</p>
      </div>
    )
  }

  return null
}

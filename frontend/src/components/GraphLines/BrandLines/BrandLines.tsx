import { useContext } from '~contexts'
import { colors } from '~utils'
import { GraphLine } from '../GraphLine'

interface BrandLinesProps {
  onClick: (newLine: DataLine) => void
}

export const BrandLines = ({ onClick }: BrandLinesProps) => {
  const { topListBrands, activeBrands } = useContext()
  return (
    <>
      {topListBrands?.map((line, i) => {
        const color = colors[i % colors.length]
        const style = activeBrands.find(
          (activeLine) => activeLine.lineId === line.brand_id,
        )
          ? { borderColor: color }
          : {}
        return (
          <GraphLine
            style={style}
            id={line.brand_id}
            onClick={onClick}
            title={line.brand_name}
            diff={{ weekly: line.weekly_diff, monthly: line.monthly_diff }}
            color={color}
            key={line.brand_id}
          />
        )
      })}
    </>
  )
}

import * as React from 'react'
import s from '../GraphLines.module.scss'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { GraphLine } from '../GraphLine'

interface CategoryLinesProps {
  onClick: (line: any) => void
}

export const CategoryLines = ({ onClick }: CategoryLinesProps) => {
  const { topListCategories, activeCategories } = useContext()
  return (
    <>
      {topListCategories?.map((line, i) => {
        const color = colors[i % colors.length]
        const style = activeCategories.includes(line.category_id)
          ? { borderColor: color }
          : {}
        return (
          <GraphLine
            style={style}
            id={line.category_id}
            onClick={onClick}
            title={line.category_name}
            diff={{ weekly: line.weekly_diff, monthly: line.monthly_diff }}
            color={color}
            key={line.category_id}
          />
        )
      })}
    </>
  )
}

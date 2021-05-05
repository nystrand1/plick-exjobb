import * as React from 'react'
import { useContext } from '~contexts'
import { colors } from '~utils'
import { GraphLine } from '../GraphLine'

interface QueryLinesProps {
  onClick: (id: any) => void
}

export const QueryLines = ({ onClick }: QueryLinesProps) => {
  const { topListQueries, activeQueries } = useContext()

  return (
    <>
      {topListQueries?.map((line, i) => {
        const color = colors[i % colors.length]
        const style = activeQueries.includes(line.query) ? { borderColor: color } : {}
        return (
          <GraphLine
            key={line.query}
            style={style}
            id={line.query}
            onClick={onClick}
            title={line.query}
            diff={{ weekly: line.weekly_diff, monthly: line.monthly_diff }}
            color={color}
          />
        )
      })}
    </>
  )
}

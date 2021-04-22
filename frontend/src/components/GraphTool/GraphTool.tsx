import * as React from 'react'
import s from './GraphTool.module.scss'
import { LargeButton, DateSelect, DropDown, GraphLines, LineGraph } from '~components'
import { useContext } from '~contexts'

export const GraphTool = () => {
  const [graphHeight, setHeight] = React.useState(0)
  const [graphWidth, setWidth] = React.useState(0)
  const graphRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (graphRef.current) {
      setHeight(graphRef.current?.getBoundingClientRect().height)
      setWidth(graphRef.current?.getBoundingClientRect().width)
    }
  }, [])

  const {
    startDate,
    endDate,
    resolution,
    setStartDate,
    setEndDate,
    setResolution,
  } = useContext()
  const [activeType, setactiveType] = React.useState<'queries' | 'brands' | 'categories'>(
    'queries',
  )
  const options = ['kvart', 'timme', 'dag', 'vecka', 'månad']
  return (
    <div className="col-12">
      <div className={s.graphToolWrapper}>
        <div className={s.topSection}>
          <div className={s.typeSelection}>
            <LargeButton
              active={activeType === 'queries'}
              onClick={() => setactiveType('queries')}
            >
              Queries
            </LargeButton>
            <LargeButton
              active={activeType === 'brands'}
              onClick={() => setactiveType('brands')}
            >
              Brands
            </LargeButton>
            <LargeButton
              active={activeType === 'categories'}
              onClick={() => setactiveType('categories')}
            >
              Categories
            </LargeButton>
          </div>
          <div className={s.dateSelection}>
            <DateSelect
              title={'FRÅN'}
              onChange={(date: Date) => setStartDate(date)}
              startDate={startDate}
            />
            <DateSelect
              title={'TILL'}
              onChange={(date: Date) => setEndDate(date)}
              startDate={endDate}
            />
            <DropDown
              options={options}
              title={'UPPLÖSNING'}
              onChange={setResolution}
              value={resolution}
            />
          </div>
        </div>
        <div className="row">
          <div className={`${s.graphLines} col-4`}>
            <GraphLines />
          </div>
          <div className={`${s.lineGraph} col-8`} ref={graphRef}>
            <LineGraph height={graphHeight} width={graphWidth} />
          </div>
        </div>
      </div>
    </div>
  )
}
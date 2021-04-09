import * as React from 'react'
import s from './GraphTool.module.scss'
import { LargeButton, DateSelect } from '~components'
import { queries } from '@testing-library/dom'
import { useContext } from '~contexts'
import DatePicker from 'react-datepicker'
import { DropDown } from '~components/shared'

export const GraphTool = () => {
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
      </div>
    </div>
  )
}

import * as React from 'react'
import s from './TopList.module.scss'
import { months, getPastDate } from '~utils'
import { TopListEntry, DropDown } from '~components'
import { useContext } from '~contexts'

interface TopListProps {
  type: 'searchTerms' | 'brands' | 'categories'
}

export const TopList = ({ type }: TopListProps) => {
  const { topListSearchTerms, topListBrands, topListCategories } = useContext()
  const [time, setTime] = React.useState('1 vecka')
  let title = ''

  if (type === 'searchTerms') {
    title = 'Söktermer'
  }
  if (type === 'brands') {
    title = 'Märken'
  }
  if (type === 'categories') {
    title = 'Kategorier'
  }

  const getTimeInterval = () => {
    const today = new Date('2021-03-15')
    let pastDate
    switch (time) {
      case '1 månad':
        pastDate = getPastDate(31, today)
        break
      case '2 veckor':
        pastDate = getPastDate(14, today)
        break
      case '1 vecka':
      default:
        pastDate = getPastDate(7, today)
    }
    const endDate = today.getDate() + ' ' + months[today.getMonth()]
    const startDate = pastDate.getDate() + ' ' + months[pastDate.getMonth()]
    return startDate + ' - ' + endDate
  }

  const options = ['1 vecka', '2 veckor', '1 månad']

  const getDiff = (entry) => {
    switch (time) {
      case '1 månad':
        return { diff: entry.monthly_diff, diffPercentage: entry.monthly_diff_percentage }
      case '1 vecka':
        return { diff: entry.weekly_diff, diffPercentage: entry.weekly_diff_percentage }
      case '1 dag':
        return null
    }
  }

  const renderTopList = () => {
    switch (type) {
      case 'searchTerms':
        return (
          <>
            {topListSearchTerms &&
              topListSearchTerms.map((entry, index) => {
                const entryDiff = getDiff(entry)
                return (
                  <TopListEntry
                    query={entry.query}
                    index={index + 1}
                    key={`${entry.query}_${index}`}
                    diff={entryDiff?.diff}
                    diffPercentage={entryDiff?.diffPercentage}
                    words={entry.similar_queries}
                  />
                )
              })}
          </>
        )
      case 'brands':
        return (
          <>
            {topListBrands &&
              topListBrands.map((entry, index) => {
                const entryDiff = getDiff(entry)
                return (
                  <TopListEntry
                    query={entry.brand_name}
                    index={index + 1}
                    key={`${entry.brand_name}_${index}`}
                    diff={entryDiff?.diff}
                    diffPercentage={entryDiff?.diffPercentage}
                  />
                )
              })}
          </>
        )
      case 'categories':
      default:
        return (
          <>
            {topListCategories &&
              topListCategories.map((entry, index) => {
                const entryDiff = getDiff(entry)
                return (
                  <TopListEntry
                    query={entry.category_name}
                    index={index + 1}
                    key={`${entry.category_name}_${index}`}
                    diff={entryDiff?.diff}
                    diffPercentage={entryDiff?.diffPercentage}
                  />
                )
              })}
          </>
        )
    }
  }

  if (type === 'searchTerms' && !topListSearchTerms) {
    return <div>Loading...</div>
  }

  if (type === 'brands' && !topListBrands) {
    return <div>Loading...</div>
  }

  if (type === 'categories' && !topListCategories) {
    return <div>Loading...</div>
  }

  return (
    <div className="col-lg-6 col-xl-4">
      <div className={`${s.topListWrapper}`}>
        <div className={s.header}>
          <h2 className={s.title}>{title}</h2>
          <p className={s.date}>{getTimeInterval()}</p>
          <DropDown options={options} value={time} onChange={setTime} />
        </div>
        <div>
          <div className={s.entries}>{renderTopList()}</div>
        </div>
        <button className={s.showMoreButton}>Visa top 50</button>
      </div>
    </div>
  )
}

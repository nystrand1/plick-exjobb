import * as React from 'react'
import s from './TopList.module.scss'
import { months, getPastDate } from '~utils'
import { TopListEntry, DropDown } from '~components'
import { useContext } from '~contexts'

interface TopListProps {
  type: 'searchTerms' | 'brands' | 'categories'
}

export const TopList = ({ type }: TopListProps) => {
  const {
    topListQueries,
    topListBrands,
    topListCategories,
    queriesTime,
    setQueriesTime,
    brandsTime,
    setBrandsTime,
    categoriesTime,
    setCategoriesTime,
  } = useContext()
  const [maxLength, setMaxLength] = React.useState(4)
  let title = ''
  let time = ''

  if (type === 'searchTerms') {
    title = 'Söktermer'
    time = queriesTime
  }
  if (type === 'brands') {
    title = 'Märken'
    time = brandsTime
  }
  if (type === 'categories') {
    title = 'Kategorier'
    time = categoriesTime
  }

  const showMore = () => {
    setMaxLength(maxLength + 2)
  }

  const setTime = (time: string) => {
    if (type === 'searchTerms') {
      setQueriesTime(time)
    }
    if (type === 'brands') {
      setBrandsTime(time)
    }
    if (type === 'categories') {
      setCategoriesTime(time)
    }
  }

  const getTimeInterval = () => {
    const today = new Date('2021-04-18')
    let endDate = today.getDate() + ' ' + months[today.getMonth()]
    let pastDate
    switch (time) {
      case '1 månad':
        pastDate = getPastDate(31, today)
        break
      case 'nästa vecka':
        pastDate = new Date(today)
        today.setDate(today.getDate() + 7)
        endDate = today.getDate() + ' ' + months[today.getMonth()]
        break
      case '1 vecka':
      default:
        pastDate = getPastDate(7, today)
    }
    const startDate = pastDate.getDate() + ' ' + months[pastDate.getMonth()]
    return startDate + ' - ' + endDate
  }

  const options = ['1 vecka', '1 månad', 'nästa vecka']

  const getDiff = (entry) => {
    switch (time) {
      case '1 månad':
        return { diff: entry.monthly_diff, diffPercentage: entry.monthly_diff_percentage }
      case '1 vecka':
        return { diff: entry.weekly_diff, diffPercentage: entry.weekly_diff_percentage }
      case 'nästa vecka':
        return { diff: entry.weekly_diff, diffPercentage: entry.weekly_diff_percentage }
    }
  }

  const renderLoading = () => {
    return <div className={s.loading}>Laddar...</div>
  }

  const renderTopList = () => {
    switch (type) {
      case 'searchTerms':
        return (
          <>
            {topListQueries
              ? topListQueries.slice(0, maxLength).map((entry, index) => {
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
                })
              : renderLoading()}
            {topListQueries && topListQueries?.length > maxLength && (
              <button className={s.showMoreButton} onClick={() => showMore()}>
                Visa fler
              </button>
            )}
          </>
        )
      case 'brands':
        return (
          <>
            {topListBrands
              ? topListBrands.slice(0, maxLength).map((entry, index) => {
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
                })
              : renderLoading()}
            {topListBrands && topListBrands?.length > maxLength && (
              <button className={s.showMoreButton} onClick={() => showMore()}>
                Visa fler
              </button>
            )}
          </>
        )
      case 'categories':
      default:
        return (
          <>
            {topListCategories
              ? topListCategories.slice(0, maxLength).map((entry, index) => {
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
                })
              : renderLoading()}
            {topListCategories && topListCategories?.length > maxLength && (
              <button className={s.showMoreButton} onClick={() => showMore()}>
                Visa fler
              </button>
            )}
          </>
        )
    }
  }

  return (
    <div className="col-lg-6 col-xl-4">
      <div className={`${s.topListWrapper}`}>
        <div className={s.header}>
          <h2 className={s.title}>{title}</h2>
          <p className={s.date}>{getTimeInterval()}</p>
          <DropDown options={options} value={time} onChange={setTime} />
        </div>
        <div className={s.dataTitles}>
          <div className={s.data}>DIFF</div>
          <div>DIFF %</div>
        </div>
        <div>
          <div className={s.entries}>{renderTopList()}</div>
        </div>
      </div>
    </div>
  )
}

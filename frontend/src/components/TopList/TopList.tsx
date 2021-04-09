import * as React from 'react'
import s from './TopList.module.scss'
import { months, getPastDate } from '~utils'
import { TopListEntry, DropDown } from '~components'
import Shoes from '~static/images/shoes.jpeg'

interface TopListProps {
  type: 'queries' | 'brands' | 'categories'
}

export const TopList = ({ type }: TopListProps) => {
  const [time, setTime] = React.useState('1 vecka')
  let title = ''

  if (type === 'queries') {
    title = 'Söktermer'
  }
  if (type === 'brands') {
    title = 'Märken'
  }
  if (type === 'categories') {
    title = 'Kategorier'
  }

  const getTimeInterval = () => {
    const today = new Date()
    let pastDate
    switch (time) {
      case '1 månad':
        pastDate = getPastDate(31)
        break
      case '2 veckor':
        pastDate = getPastDate(14)
        break
      case '1 vecka':
      default:
        pastDate = getPastDate(7)
    }
    const endDate = today.getDate() + ' ' + months[today.getMonth()]
    const startDate = pastDate.getDate() + ' ' + months[pastDate.getMonth()]
    return startDate + ' - ' + endDate
  }

  const topList = [
    {
      query: 'Skor',
      metric: 1337,
      image: Shoes,
      words: ['Nike', 'Skor 38', 'Air Force 1', 'Adidas'],
    },
    {
      query: 'Tröjor',
      metric: 1336,
      image: Shoes,
    },
    {
      query: 'Byxor',
      metric: 1335,
      image: Shoes,
    },
    { query: 'Mössor', metric: 1334, image: Shoes },
  ]

  const options = ['1 vecka', '2 veckor', '1 månad']

  return (
    <div className="col-lg-6 col-xl-4">
      <div className={`${s.topListWrapper}`}>
        <div className={s.header}>
          <h2 className={s.title}>{title}</h2>
          <p className={s.date}>{getTimeInterval()}</p>
          <DropDown options={options} value={time} onChange={setTime} />
        </div>
        <div>
          <div className={s.entries}>
            {topList.map((entry, index) => (
              <TopListEntry
                {...entry}
                index={index + 1}
                key={`${entry.query}_${index}`}
              />
            ))}
          </div>
        </div>
        <button className={s.showMoreButton}>Visa top 50</button>
      </div>
    </div>
  )
}

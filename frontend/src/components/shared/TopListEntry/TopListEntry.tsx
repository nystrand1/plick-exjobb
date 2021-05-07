import * as React from 'react'
import s from './TopListEntry.module.scss'
import { Api } from '~services'
import Loading from '~static/images/loading.gif'
import { useContext } from '~contexts'

interface TopListEntryProps {
  query: string
  diff?: number
  diffPercentage?: number
  index: number
  image?: string
  words?: string[]
}

export const TopListEntry = ({
  query,
  diff,
  diffPercentage,
  index,
  words,
}: TopListEntryProps) => {
  const { exampleAds, setModalEntry } = useContext()
  const [image, setImage] = React.useState()
  React.useEffect(() => {
    const entryQuery = query.toLowerCase()
    Api.exampleAds({ query: entryQuery, limit: 2 }).then((data) => {
      const ads = data.blocks.map((block) => block.data.ads).flat(1)

      if (!exampleAds.find((ad) => ad.key === entryQuery)) {
        exampleAds.push({ key: entryQuery, ads })
      }

      setImage(ads[Math.floor(Math.random() * ads.length)].ad_photos[0].photo)
    })
  }, [query, exampleAds])

  return (
    <button className={s.entryWrapper} onClick={() => setModalEntry(query.toLowerCase())}>
      <div className={s.text}>
        <h3 className={s.index}>{index}</h3>
        <div className={s.queryWrapper}>
          <div className={s.queryAndMetric}>
            <div className={s.query}>{query}</div>
            <div className={s.metric}>
              {diff && (
                <div className={s.diff}>
                  {Math.round(diff) > 0 ? '+' : ''}
                  {Math.round(diff)}
                </div>
              )}
              {diffPercentage && (
                <div className={s.diffPercentage}>
                  ({Math.round(diffPercentage) > 0 ? '+' : ''}
                  {Math.round(diffPercentage)}%)
                </div>
              )}
            </div>
          </div>
          {words && words?.length > 0 && (
            <div className={s.words}>{words.join(', ')}</div>
          )}
        </div>
      </div>
      <img src={image || Loading} alt={query} className={s.image} />
    </button>
  )
}

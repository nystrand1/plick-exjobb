import * as React from 'react'
import s from './TopListEntry.module.scss'
import { ReactComponent as ShowMore } from '~static/svg/more.svg'
import { Api } from '~services'
import Loading from '~static/images/loading.gif'

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
  const [image, setImage] = React.useState()
  React.useEffect(() => {
    Api.exampleAds({ query: query.toLowerCase(), limit: 1 }).then((data) => {
      const ads = data.blocks[0].data.ads
      setImage(ads[Math.floor(Math.random() * ads.length)].ad_photos[0].photo)
      if (query === 'xs') {
        console.log(data)
      }
    })
  }, [query])

  return (
    <button className={s.entryWrapper} onClick={() => console.log('display entry info')}>
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
      <div className={s.imageWrapper}>
        <img src={image || Loading} alt={query} className={s.image} />
        <ShowMore className={s.showMore} />
      </div>
    </button>
  )
}

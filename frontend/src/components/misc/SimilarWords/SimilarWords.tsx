import { useEffect } from 'react'
import s from './SimilarWords.module.scss'

interface SimilarWordsProps {
  words?: string[]
}

export const SimilarWords = ({ words }: SimilarWordsProps) => {
  useEffect(() => {
    console.log(words)
  }, []);
  return (
    <div className={s.similarWords}>
      {words?.map((word) => {
        return <p>{word}</p>
      })}
    </div>
  )
}

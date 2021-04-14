import * as React from 'react'
import s from './LargeButton.module.scss'

interface LargeButtonProps extends React.ComponentProps<'button'> {
  active: boolean
}

export const LargeButton = ({ active, children, ...other }: LargeButtonProps) => {
  const buttonClasses = [s.largeButton]

  if (active) {
    buttonClasses.push(s.active)
  }
  return (
    <button className={buttonClasses.join(' ')} {...other}>
      {children}
    </button>
  )
}

export const months = [
  'januari',
  'februari',
  'mars',
  'april',
  'maj',
  'juni',
  'juli',
  'augusti',
  'september',
  'oktober',
  'november',
  'december',
]

export const getPastDate = (numberOfDays: number) => {
  const today = new Date()
  const day = 24 * 60 * 60 * 1000
  return new Date(today.getTime() - numberOfDays * day)
}

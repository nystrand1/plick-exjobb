interface IData {
  count: number
  query: string
  timeInterval: string
  trend: number
}

interface ICountRequestData {
  query?: string,
  interval_mins?: number,
  start_date?: Date,
  end_date?: Date,
  degrees?: number,
}
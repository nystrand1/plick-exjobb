interface Data {
  count: number
  query: string
  timeInterval: string
  trend: number
}

interface CountRequestData {
  query?: string,
  interval_mins?: number,
  start_date?: Date,
  end_date?: Date,
}
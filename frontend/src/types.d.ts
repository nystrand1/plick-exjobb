interface IDataSet {
  count: number
  query: string
  timeInterval: string
  trends: { [key: string]: number }
}

interface IData {
  dataset: IDataSet[]
  similarWords: string[]
  modelScores: { [key: string]: number }
}

interface ICountRequestData {
  query?: string
  trunc_by?: string
  start_date?: Date
  end_date?: Date
  degrees?: number
}

interface ITrendingRequestData {
  limit?: number
}


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

interface IExampleAdsRequestData {
  query?: string
  limit?: number
}

interface ITopListEntry {
  model_short: number[]
  model_long: number[]
  weekly_diff: number
  weekly_diff_percentage: number
  monthly_diff: number
  monthly_diff_percentage: number
}

interface ITopListSearchTerm extends ITopListEntry {
  query: string
  similar_queries: string[]
}

interface ITopListBrand extends ITopListEntry {
  brand_id: number
  brand_name: string
}

interface ITopListCategory extends ITopListEntry {
  category_id: number
  category_name: string
}

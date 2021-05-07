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
  limit?: number,
  future?: boolean
}

interface IExampleAdsRequestData {
  query?: string
  limit?: number
}

interface IQueryDatasetData {
  query: string
}

interface IBrandTimeseriesData {
  brand_ids: number[]
  resolution: string
}

interface ICategoryTimeseriesData {
  category_ids: number[]
  resolution: string
}

interface IQueryTimeseriesData {
  query_ids: string[]
  resolution: string
}

interface IDataPoint {
  count: number
  time_interval: string
  trends: {}
}

interface DataLine {
  lineId: string | number
  displayTrend: boolean
  displayPrediction: boolean
}

interface ITimeSeries {
  created_at: string
  model_long: number[]
  model_mid: number[]
  model_short: number[]
  model_lstm: number[]
  model_sarima: number[]
  similar_queries: string[]
  time_series_min: []
  time_series_hour: IDataPoint[]
  time_series_day: IDataPoint[]
  time_series_week: IDataPoint[]
  time_series_month: IDataPoint[]
  updated_at: string
}

interface ITimeSeriesSearchTerms extends ITimeSeries {
  query: string
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

import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:5000'

export class Api {
  static async countIntervalGrouped(data: ICountRequestData) {
    return this.post('count-interval-grouped', data)
  }

  static async countIntervalIndividual(data: ICountRequestData) {
    return this.post('count-interval-individual', data)
  }

  static async linearRegression(data: ICountRequestData) {
    return this.post('linear-regression', data)
  }

  static async armaRegression(data: ICountRequestData) {
    return this.post('arma-regression', data)
  }

  static async sarmaRegression(data: ICountRequestData) {
    return this.post('sarma-regression', data)
  }

  static async autoSarima(data: ICountRequestData) {
    return this.post('auto-sarima', data)
  }

  static async trendingSearchTerms(data?: ITrendingRequestData) {
    return this.post('trending-words', data)
  }

  static async trendingBrands(data?: ITrendingRequestData) {
    return this.post('trending-brands', data)
  }

  static async trendingCategories(data?: ITrendingRequestData) {
    return this.post('trending-categories', data)
  }

  static async exampleAds(data?: IExampleAdsRequestData) {
    return this.post('example-ads', data)
  }

  static async queryDataset(data: IQueryDatasetData) {
    return this.post('query-dataset', data)
  }

  static async getBrandTimeseries(data: IBrandTimeseriesData) {
    return this.post('get-brand-timeseries', data)
  }

  static async getCategoryTimeseries(data: ICategoryTimeseriesData) {
    return this.post('get-category-timeseries', data)
  }

  static async getQueryTimeseries(data: IQueryTimeseriesData) {
    return this.post('get-query-timeseries', data)
  }

  static async get(endpoint: string, data = {}) {
    const response = await axios.get(endpoint, data)
    return response.data
  }

  static async post(endpoint: string, data = {}) {
    const response = await axios.post(endpoint, data)
    return response.data
  }
}

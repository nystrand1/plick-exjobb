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

  static async trendingWords(data?: ITrendingRequestData) {
    return this.post('trending-words', data)
  }
  
  static async trendingBrands() {
    return this.post('trending-brands')
  }
  
  static async trendingCategories() {
    return this.post('trending-categories')
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

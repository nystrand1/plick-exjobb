const axios = require("axios").default;

axios.defaults.baseURL = "http://localhost:5000";

export class Api {
  static async countIntervalGrouped(data: CountRequestData) {
    return this.post("count-interval-grouped", data);
  }

  static async countIntervalIndividual(data: CountRequestData) {
    return this.post("count-interval-individual", data);
  }

  static async linearRegression(data: CountRequestData) {
    return this.post("linear-regression", data);
  }

  static async get(endpoint : string, data = {}) {
    const response = await axios.get(endpoint, data);
    return response.data;
  }

  static async post(endpoint : string, data = {}) {
    const response = await axios.post(endpoint, data);
    return response.data;
  }
}

const axios = require("axios").default;

axios.defaults.baseURL = "http://localhost:5000";

export default class Api {

  static async get(endpoint, data = {}) {
    const response = await axios.get(endpoint, data);
    return response.data;
  }

  static async post(endpoint, data = {}) {
    const response = await axios.post(endpoint, data);
    return response.data;
  }
}

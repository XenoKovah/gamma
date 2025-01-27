import axios, { CreateAxiosDefaults } from "axios";


// const config: CreateAxiosDefaults = {
//   baseURL: process.env.REACT_APP_PUBLIC_URL || 'http://localhost:8000/',
// };

const config: CreateAxiosDefaults = {
  baseURL: 'http://0.0.0.0:9700/', // pass local URL for the local development, should be changed
};

const axiosInstance = axios.create(config);

export default axiosInstance;

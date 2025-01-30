import axios from 'axios';

const config = {
  baseURL: 'http://0.0.0.0:9700/', // pass local URL for the local development, should be changed
};

const axiosInstance = axios.create(config);

export default axiosInstance;

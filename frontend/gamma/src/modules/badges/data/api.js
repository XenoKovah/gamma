import axios from 'axios';

import { API_ROUTES } from './constants';

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchBadgesData = async () => {
  const { data } = await axios.get(API_ROUTES.BADGES);
  return data;
};

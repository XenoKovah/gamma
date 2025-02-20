import axios from 'axios';

import { API_ROUTES, REQUEST_HEADERS } from './constants';
import {
  fileToBase64,
  preparePayload,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
} from './utils';

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchBadgesData = async () => {
  const { data } = await axios.get(API_ROUTES.BADGES);
  return Array.isArray(data) ? convertKeysToCamelCase(data).reverse() : [];
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchCoursesData = async () => {
  const { data } = await axios.get(API_ROUTES.COURSES);
  return convertKeysToCamelCase(data);
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchOrganizationsData = async () => {
  const { data } = await axios.get(API_ROUTES.ORGANIZATIONS);
  return convertKeysToCamelCase(data);
};

/**
 * Fetches actions data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchActionsData = async () => {
  const { data } = await axios.get(API_ROUTES.ACTIONS);
  return convertKeysToCamelCase(data);
};

/**
 * Creates a new badge.
 * @param {Object} badgeData - The badge data to be sent in the request body.
 * @returns {Promise<Object>} The response from the API.
 */
export const createBadge = async (badgeData) => {
  try {
    const cleanedData = preparePayload(structuredClone(badgeData));

    const requestData = {
      ...cleanedData,
      image: await fileToBase64(cleanedData.image),
    };

    const response = await axios.post(API_ROUTES.BADGES, convertKeysToSnakeCase(requestData), {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return response.data;
  } catch (error) {
    console.error('Error creating badge:', error); // eslint-disable-line no-console
    throw error;
  }
};

/**
 * Deletes a badge by its ID.
 * @param {number|string} badgeId - The ID of the badge to be deleted.
 * @returns {Promise<Object>} The response from the API.
 */
export const deleteBadge = async (badgeId) => {
  const response = await axios.delete(`${API_ROUTES.BADGES}${badgeId}/`, {
    headers: { ...REQUEST_HEADERS },
    withCredentials: true,
  });

  return response.data;
};

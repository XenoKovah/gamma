import axios from 'axios';

import { API_ROUTES, REQUEST_HEADERS } from './constants';
import {
  logError,
  fileToBase64,
  preparePayload,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
  processReceivedPayload,
} from './utils';

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchBadgesData = async () => {
  try {
    const { data } = await axios.get(API_ROUTES.BADGES);

    const processedData = Array.isArray(data) ? convertKeysToCamelCase(data) : [];

    const result = processedData.map(processReceivedPayload);

    return result;
  } catch (error) {
    logError('Error fetching badges data:', error);
    throw error;
  }
};

/**
 * Updates an existing badge with the provided data.
 *
 * @async
 * @param {string|number} badgeId - The ID of the badge to update.
 * @param {Object} badgeData - The updated badge data.
 * @param {string} [badgeData.image] - The image URL (if already uploaded).
 * @param {File} [badgeData.image] - The image file to be uploaded.
 * @returns {Promise<Object>} The updated badge data from the API response.
 * @throws {Error} If the request fails.
 */
export const editBadge = async (badgeId, badgeData) => {
  try {
    const cleanedData = preparePayload(structuredClone(badgeData));

    if (typeof cleanedData.image === 'string') {
      delete cleanedData.image;
    }

    if (cleanedData.image instanceof File) {
      cleanedData.image = await fileToBase64(cleanedData.image);
    }

    const requestData = convertKeysToSnakeCase(cleanedData);

    const response = await axios.patch(`${API_ROUTES.BADGES}${badgeId}/`, requestData, {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return response.data;
  } catch (error) {
    logError('Error editing badge:', error);
    throw error;
  }
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchCoursesData = async () => {
  try {
    const { data } = await axios.get(API_ROUTES.COURSES);
    return convertKeysToCamelCase(data);
  } catch (error) {
    logError('Error fetching courses data:', error);
    throw error;
  }
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The badge data.
 */
export const fetchOrganizationsData = async () => {
  try {
    const { data } = await axios.get(API_ROUTES.ORGANIZATIONS);
    return convertKeysToCamelCase(data);
  } catch (error) {
    logError('Error fetching organizations data:', error);
    throw error;
  }
};

/**
 * Fetches actions data from the API.
 * @returns {Promise<Object>} The actions data.
 */
export const fetchActionsData = async () => {
  try {
    const { data } = await axios.get(API_ROUTES.ACTIONS);
    return convertKeysToCamelCase(data);
  } catch (error) {
    logError('Error fetching actions data:', error);
    throw error;
  }
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
    logError('Error creating badge:', error);
    throw error;
  }
};

/**
 * Deletes a badge by its ID.
 * @param {number|string} badgeId - The ID of the badge to be deleted.
 * @returns {Promise<Object>} The response from the API.
 */
export const deleteBadge = async (badgeId) => {
  try {
    const response = await axios.delete(`${API_ROUTES.BADGES}${badgeId}/`, {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return response.data;
  } catch (error) {
    logError('Error deleting badge:', error);
    throw error;
  }
};

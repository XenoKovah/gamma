import axios from 'axios';

import { API_ROUTES, REQUEST_HEADERS } from './constants';
import { convertKeysToCamelCase, convertKeysToSnakeCase } from './utils';

/**
 * Fetches avatar sets data from the API.
 * @returns {Promise<Object>} The avatar sets data.
 */
export const fetchAvatarSetsData = async () => {
  const { data } = await axios.get(API_ROUTES.AVATAR_SET);
  return Array.isArray(data) ? convertKeysToCamelCase(data).reverse() : [];
};

/**
 * Deletes a avatar set by its ID.
 * @param {number|string} avatarSetId - The ID of the avatar set to be deleted.
 * @returns {Promise<Object>} The response from the API.
 */
export const deleteAvatarSet = async (avatarSetId) => {
  const response = await axios.delete(`${API_ROUTES.AVATAR_SET}${avatarSetId}/`, {
    headers: { ...REQUEST_HEADERS },
    withCredentials: true,
  });

  return convertKeysToCamelCase(response.data);
};

/**
 * Creates a new avatar set by sending a POST request to the API.
 * @param {Object} avatarSetData - The data for the new avatar set.
 * @returns {Promise<Object>} A promise that resolves to the created avatar set with keys in camelCase.
 * @throws {Error} Throws an error if the request fails.
 */
export const createAvatarSet = async (avatarSetData) => {
  try {
    const response = await axios.post(API_ROUTES.AVATAR_SET, convertKeysToSnakeCase(avatarSetData), {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error creating badge:', error); // eslint-disable-line no-console
    throw error;
  }
};

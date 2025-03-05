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

/**
 * Updates an existing avatar set with new data.
 *
 * @async
 * @function updateAvatarSet
 * @param {Object} avatarSetData - The data to update the avatar set.
 * @param {string} avatarSetData.id - The unique identifier of the avatar set to be updated.
 * @param {string} [avatarSetData.title] - The title of the avatar set.
 * @param {Array<Object>} [avatarSetData.avatars] - An array of avatar objects associated with the set.
 * @param {Array<string>} [avatarSetData.useInCourses] - A list of course IDs where the avatar set is used.
 * @param {boolean} [avatarSetData.isDraft] - Indicates if the avatar set is in draft mode.
 * @returns {Promise<Object>} A promise resolving to the updated avatar set with camelCase keys.
 * @throws {Error} Throws an error if the update request fails.
 */
export const updateAvatarSet = async (avatarSetData) => {
  const { id } = avatarSetData;
  try {
    const response = await axios.patch(`${API_ROUTES.AVATAR_SET}${id}/`, convertKeysToSnakeCase(avatarSetData), {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    throw error;
  }
};

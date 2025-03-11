import axios from 'axios';

import { API_ROUTES, REQUEST_HEADERS } from './constants';
import {
  preparePayload,
  readFileAsBase64,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
  processReceivedAvatarSets,
  convertImageToBase64,
} from './utils';

// TODO: temp solution to show student experience with avatars.
/**
 * Fetches student avatar data from the API.
 * @returns {Promise<Object>} The student avatar data.
 */
export const fetchStudentAvatarData = async (avatarSetIdParams, studentUsername) => {
  const queryParams = studentUsername ? `?username=${encodeURIComponent(studentUsername)}` : '';
  const { data } = await axios.get(`${API_ROUTES.AVATAR_SET}${avatarSetIdParams}/${queryParams}`);

  return convertKeysToCamelCase(data);
};

/**
 * Fetches avatar sets data from the API.
 * @returns {Promise<Object>} The avatar sets data.
 */
export const fetchAvatarSetsData = async () => {
  const { data } = await axios.get(API_ROUTES.AVATAR_SET);
  return Array.isArray(data)
    ? processReceivedAvatarSets(convertKeysToCamelCase(data))
    : [];
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
  const { id, avatars } = avatarSetData;

  const formattedAvatarsData = avatars
    ? await Promise.all(
      avatars.map(async (avatar) => {
        const clonedAvatar = structuredClone(avatar);

        if (clonedAvatar.image) {
          clonedAvatar.image = await convertImageToBase64(clonedAvatar.image);
        }

        return preparePayload(clonedAvatar);
      }),
    )
    : undefined;

  const preparedAvatarSetData = {
    ...convertKeysToSnakeCase(avatarSetData),
    ...(formattedAvatarsData ? { avatars: formattedAvatarsData } : {}),
  };

  try {
    const response = await axios.patch(
      `${API_ROUTES.AVATAR_SET}${id}/`,
      convertKeysToSnakeCase(preparedAvatarSetData),
      {
        headers: { ...REQUEST_HEADERS },
        withCredentials: true,
      },
    );

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    throw error;
  }
};

/**
 * Finishes updating for an existing avatar set.
 *
 * @async
 * @function finishUpdatingAvatarSet
 * @param {string} id - The unique identifier of the avatar set to be updated.
 * @returns {Promise<Object>} A promise resolving to the finished updating avatar set.
 * @throws {Error} Throws an error if the update request fails.
 */
export const finishUpdatingAvatarSet = async (id) => {
  try {
    const response = await axios.patch(API_ROUTES.GET_AVATAR_SET_FINISH(id), {}, {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    throw error;
  }
};

/**
 * Deletes an avatar by its ID.
 *
 * @async
 * @function deleteAvatarById
 * @param {number|string} avatarId - The ID of the avatar to delete.
 * @returns {Promise<Object>} - The response data with keys converted to camelCase.
 * @throws {Error} - Throws an error if the request fails.
 */
export const deleteAvatarById = async (avatarId) => {
  try {
    const response = await axios.delete(`${API_ROUTES.AVATAR}${avatarId}/`, {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    throw error;
  }
};

/**
 * Updates an avatar by its ID with the provided data.
 *
 * @async
 * @function updateAvatarById
 * @param {number|string} avatarId - The ID of the avatar to update.
 * @param {Object} avatarData - The new avatar data to update.
 * @param {string} [avatarData.title] - The title of the avatar.
 * @param {string} [avatarData.description] - The description of the avatar.
 * @param {string|File|null} [avatarData.image] - The avatar image, which can be a URL, a File object, or null.
 * @param {Array<Object>} [avatarData.rules] - The rules associated with the avatar.
 * @returns {Promise<Object>} - The updated avatar data with keys converted to camelCase.
 * @throws {Error} - Throws an error if the request fails.
 */
export const updateAvatarById = async (avatarId, avatarData) => {
  try {
    const cleanedData = preparePayload(structuredClone(avatarData));

    if (typeof cleanedData.image === 'string') {
      delete cleanedData.image;
    }

    if (cleanedData.image instanceof File) {
      cleanedData.image = await readFileAsBase64(cleanedData.image);
    }

    const requestData = convertKeysToSnakeCase(cleanedData);

    const response = await axios.patch(`${API_ROUTES.AVATAR}${avatarId}/`, requestData, {
      headers: { ...REQUEST_HEADERS },
      withCredentials: true,
    });

    return convertKeysToCamelCase(response.data);
  } catch (error) {
    console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    throw error;
  }
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The courses data.
 */
export const fetchCoursesData = async () => {
  const { data } = await axios.get(API_ROUTES.COURSES);
  return convertKeysToCamelCase(data);
};

/**
 * Fetches badge data from the API.
 * @returns {Promise<Object>} The organizations data.
 */
export const fetchOrganizationsData = async () => {
  const { data } = await axios.get(API_ROUTES.ORGANIZATIONS);
  return convertKeysToCamelCase(data);
};

/**
 * Fetches actions data from the API.
 * @returns {Promise<Object>} The actions data.
 */
export const fetchActionsData = async () => {
  const { data } = await axios.get(API_ROUTES.ACTIONS);
  return convertKeysToCamelCase(data);
};

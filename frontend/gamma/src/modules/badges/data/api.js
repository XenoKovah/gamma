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
import { getGammaHeaderConfig } from '../../../utils';

/**
 * An identifier is treated as an email if it contains an "@". edX usernames
 * cannot contain "@", so this cleanly separates emails from usernames.
 */
const looksLikeEmail = (identifier) => identifier.includes('@');

/**
 * Resolve a list of assignment identifiers (edX usernames and/or emails) to
 * usernames. The gamma service stores no email, so emails are looked up against
 * the LMS accounts API (staff-only) using the LMS base URL the Django view
 * injects into the page. Non-email identifiers pass through unchanged.
 *
 * @param {string[]} identifiers - Usernames and/or emails as typed by the admin.
 * @returns {Promise<{usernames: string[], unresolved: string[]}>} `usernames`:
 *   order-preserving, de-duplicated usernames to assign; `unresolved`: emails
 *   that could not be matched to a user (or couldn't be looked up), so the caller
 *   can surface them instead of silently assigning to a bogus user.
 */
export const resolveIdentifiersToUsernames = async (identifiers) => {
  const { lmsBaseUrl } = getGammaHeaderConfig();
  const usernames = [];
  const unresolved = [];

  for (const identifier of identifiers) {
    if (!looksLikeEmail(identifier)) {
      usernames.push(identifier);
    } else if (!lmsBaseUrl) {
      unresolved.push(identifier);
    } else {
      try {
        // Staff-only LMS lookup; withCredentials sends the shared edX JWT cookie.
        // eslint-disable-next-line no-await-in-loop
        const { data } = await axios.get(`${lmsBaseUrl}/api/user/v1/accounts`, {
          params: { email: identifier },
          withCredentials: true,
        });
        const username = Array.isArray(data) && data[0]?.username;
        if (username) {
          usernames.push(username);
        } else {
          unresolved.push(identifier);
        }
      } catch (error) {
        // 404 (no such email) and any auth/CORS failure land here — surface the
        // email as unresolved rather than assigning to a bogus user.
        logError('Error resolving email to username:', error);
        unresolved.push(identifier);
      }
    }
  }

  return { usernames: [...new Set(usernames)], unresolved: [...new Set(unresolved)] };
};

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
 * Manually assigns a badge to one or more users by their user id.
 * @param {number|string} badgeId - The ID of the badge to assign.
 * @param {string[]} userUids - The GammaUser user_uids (edX usernames) to grant the badge to.
 * @returns {Promise<{granted: string[], already_assigned: string[], points_each: number}>}
 *          The API response listing which users were newly granted vs already had the badge.
 */
export const assignBadge = async (badgeId, userUids) => {
  try {
    const response = await axios.post(
      `${API_ROUTES.BADGES}${badgeId}/assign/`,
      { user_uids: userUids },
      {
        headers: { ...REQUEST_HEADERS },
        withCredentials: true,
      },
    );

    return response.data;
  } catch (error) {
    logError('Error assigning badge:', error);
    throw error;
  }
};

/**
 * Manually removes a badge from one or more users by their user id (inverse of assignBadge).
 * @param {number|string} badgeId - The ID of the badge to remove.
 * @param {string[]} userUids - The GammaUser user_uids (edX usernames) to remove the badge from.
 * @returns {Promise<{removed: string[], not_assigned: string[], points_each: number}>}
 *          The API response listing which users had the badge removed vs never had it.
 */
export const unassignBadge = async (badgeId, userUids) => {
  try {
    const response = await axios.post(
      `${API_ROUTES.BADGES}${badgeId}/unassign/`,
      { user_uids: userUids },
      {
        headers: { ...REQUEST_HEADERS },
        withCredentials: true,
      },
    );

    return response.data;
  } catch (error) {
    logError('Error unassigning badge:', error);
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

import axios from 'axios';

/**
 * Converts a File or Blob to a Base64-encoded string.
 *
 * @param {File | Blob} file - The file or blob to convert.
 * @returns {Promise<string>} A promise that resolves to a Base64 string.
 */
export const readFileAsBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onloadend = () => resolve(reader.result);
  reader.onerror = () => reject(new Error('Error reading file as Base64'));
  reader.readAsDataURL(file);
});

/**
 * Fetches an image from a URL and converts it to a Blob.
 *
 * @param {string} url - The image URL.
 * @returns {Promise<Blob | null>} A promise that resolves to a Blob or null if an error occurs.
 */
export const fetchImageAsBlob = async (url) => {
  try {
    const response = await axios.get(url, { responseType: 'blob' });
    return response.data;
  } catch (error) {
    console.error('Error fetching image:', error); // eslint-disable-line no-console
    return null;
  }
};

/**
 * Converts an image to Base64 format if needed.
 * - If the image is already in Base64 format (`data:image/...`), returns it as is.
 * - If the image is a `File` or `Blob`, reads it as Base64.
 * - If the image is a URL (`string`), fetches it and converts it to Base64.
 * - If the input is `null` or invalid, returns `null`.
 *
 * @param {string | File | Blob | null} image - The image to be converted.
 * @returns {Promise<string | null>} A promise that resolves to a Base64 string or `null` if conversion fails.
 */
export const convertImageToBase64 = async (image) => {
  if (!image) { return null; }

  if (typeof image === 'string') {
    if (image.startsWith('data:image/')) { return image; }

    const blob = await fetchImageAsBlob(image);
    return blob ? readFileAsBase64(blob) : null;
  }

  if (image instanceof File || image instanceof Blob) {
    return readFileAsBase64(image);
  }

  console.warn('Invalid image format provided:', image); // eslint-disable-line no-console
  return null;
};

/**
 * Converts a value to a number if possible, otherwise returns undefined.
 *
 * @param {*} value - The value to convert to a number
 * @returns {number|undefined} The converted number if the value can be converted,
 *                            undefined if the value is undefined, null, or cannot be converted to a number
 */
export const toNumberOrUndefined = (value) => (
  value !== undefined && value !== null && !Number.isNaN(Number(value)) ? Number(value) : undefined);

/**
 * Transforms an array of rules by converting their action properties into a specific format.
 * For each rule with an action object, it restructures the action based on eventType, count, and points.
 *
 * @param {Array<Object>} rules - The array of rules to transform
 * @param {Object} [rules[].action] - The action object within each rule
 * @param {string} [rules[].action.id] - The action's ID
 * @param {string} [rules[].action.eventType] - The type of event for the action
 * @param {number} [rules[].action.count] - The count value for the action
 * @param {number} [rules[].action.points] - The points value for the action
 * @param {*} [rules[].eventConfiguration] - The existing event configuration
 *
 * @returns {Array<Object>} An array of transformed rules where each action is converted to the format:
 *                         { [eventType]: { count?: number, points?: number } }
 */
export const transformActions = (rules) => rules.map((rule) => {
  if (rule.action && typeof rule.action === 'object') {
    const {
      id, eventType, count, points,
    } = rule.action;
    return {
      ...rule,
      action: {
        [eventType]: {
          [count ? 'count' : 'points']: toNumberOrUndefined(count) || toNumberOrUndefined(points),
        },
      },
      eventConfiguration: id ?? rule.eventConfiguration ?? null,
    };
  }
  return rule;
});

/**
 * Prepares the payload by removing temporary IDs and transforming rule actions.
 *
 * @param {Object} data - The original payload data.
 * @param {Array} data.rules - The array of rules to process.
 * @returns {Object} - The transformed payload with cleaned rules.
 */
export const preparePayload = (data) => ({
  ...data,
  rules: data.rules ? transformActions(data.rules) : undefined,
});

/**
 * Retrieves the CSRF token from the browser's cookies.
 *
 * This function searches the document's cookies for a cookie named 'csrftoken'
 * and returns its value. If the cookie is not found, it returns an empty string.
 *
 * @returns {string} The CSRF token if found, otherwise an empty string.
 */
export const getCsrfToken = () => {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
};

/**
 * Converts a snake_case string to camelCase.
 *
 * @param {string} str - The snake_case string to convert.
 * @returns {string} - The converted camelCase string.
 */
export const toCamelCase = (str) => str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());

/**
 * Converts a camelCase string to snake_case.
 *
 * @param {string} str - The camelCase string to convert.
 * @returns {string} - The converted snake_case string.
 */
export const toSnakeCase = (str) => str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

/**
 * Reverses the transformation applied by `transformActions`, converting the nested action object
 * back to a flat structure. Transforms from:
 * { [eventType]: { count: value } } or { [eventType]: { points: value } }
 * to:
 * { eventType, count, points } format
 *
 * @param {Array<{
*   action?: {
*     [eventType: string]: {
*       count?: number,
*       points?: number
*     }
*   },
*   eventConfiguration?: any,
*   [key: string]: any
* }>} rules - Array of rules with nested action objects to transform
*
* @returns {Array<{
*   action?: {
*     eventType: string,
*     count?: number,
*     points?: number
*   },
*   eventConfiguration: any|null,
*   [key: string]: any
* }>} Transformed array of rules with flattened action objects
*/
export const reverseTransformActions = (rules) => rules.map((rule) => {
  if (rule.action && typeof rule.action === 'object') {
    const [eventType, measurement] = Object.entries(rule.action)[0] || [];
    return eventType
      ? {
        ...rule,
        action: { eventType, ...measurement },
        eventConfiguration: rule.eventConfiguration ?? null,
      }
      : rule;
  }
  return rule;
});

/**
 * Processes an array of avatar sets, transforming the rules inside each avatar.
 *
 * @function processReceivedAvatarSets
 * @param {Array<Object>} avatarSets - The array of avatar sets to process.
 * @param {number} avatarSets[].id - The ID of the avatar set.
 * @param {string} avatarSets[].title - The title of the avatar set.
 * @param {Array<Object>} avatarSets[].avatars - The array of avatars in the set.
 * @param {number} avatarSets[].avatars[].id - The ID of the avatar.
 * @param {string} avatarSets[].avatars[].title - The title of the avatar.
 * @param {string} avatarSets[].avatars[].description - The description of the avatar.
 * @param {string} avatarSets[].avatars[].image - The URL of the avatar image.
 * @param {Array<Object>} avatarSets[].avatars[].rules - The rules associated with the avatar.
 * @param {Object} avatarSets[].avatars[].rules[].action - The action associated with the rule.
 * @returns {Array<Object>} - The processed avatar sets with transformed rules.
 */
export const processReceivedAvatarSets = (avatarSets) => avatarSets.map((avatarSet) => ({
  ...avatarSet,
  avatars: avatarSet.avatars.map((avatar) => ({
    ...avatar,
    rules: Array.isArray(avatar?.rules) && avatar?.rules.length > 0
      ? reverseTransformActions(avatar.rules)
      : [],
  })),
}));

/**
 * Recursively transforms the keys of an object or array using a given transformation function.
 *
 * @param {any} data - The input data to transform (can be an object, array, or primitive).
 * @param {function(string): string} transformFn - The function to apply to each key.
 * @returns {any} - The transformed object or array with updated keys.
 */
const transformObjectKeys = (data, transformFn) => {
  if (Array.isArray(data)) {
    return data.map(item => transformObjectKeys(item, transformFn));
  }
  if (data && typeof data === 'object') {
    return Object.entries(data).reduce((acc, [key, value]) => {
      if (key === 'action') {
        acc[key] = value;
      } else {
        const transformedKey = transformFn(key);
        acc[transformedKey] = transformObjectKeys(value, transformFn);
      }
      return acc;
    }, {});
  }
  return data;
};

/**
 * Converts all object keys to camelCase recursively.
 *
 * @param {any} data - The input data (can be an object, array, or primitive).
 * @returns {any} - The transformed object or array with camelCase keys.
 */
export const convertKeysToCamelCase = (data) => transformObjectKeys(data, toCamelCase);

/**
 * Converts all object keys to snake_case recursively.
 *
 * @param {any} data - The input data (can be an object, array, or primitive).
 * @returns {any} - The transformed object or array with snake_case keys.
 */
export const convertKeysToSnakeCase = (data) => transformObjectKeys(data, toSnakeCase);

/**
 * Logs an error message along with the error object to the console.
 *
 * @param {string} message - The error message to log.
 * @param {Error} [error] - The optional error object providing more details.
 */
export const logError = (message, error) => {
  console.error(`${message}`, error); // eslint-disable-line no-console
};

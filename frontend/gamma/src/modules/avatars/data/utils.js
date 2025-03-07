/**
 * Converts a File object to a Base64-encoded string.
 *
 * @param {File} file - The file to convert.
 * @returns {Promise<string>} A promise that resolves with the Base64-encoded string of the file.
 */
export const fileToBase64 = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result);
  reader.onerror = reject;
  reader.readAsDataURL(file);
});

/**
 * Recursively removes all occurrences of the `tempId` property from an object.
 * This function creates a new object without modifying the original one.
 *
 * @param {Object|Array} obj - The object or array to process.
 * @returns {Object|Array} A new object or array without `tempId` properties.
 */
export const removeTempIds = (obj) => {
  if (Array.isArray(obj)) {
    return obj.map(removeTempIds);
  }
  if (obj && typeof obj === 'object') {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      if (key !== 'tempId') {
        acc[key] = removeTempIds(value);
      }
      return acc;
    }, {});
  }
  return obj;
};

/**
 * Transforms the `action` object in each rule by making `eventType` the key and `count` its value.
 *
 * @param {Array<{ action?: {
 *  eventType: string,
 *  count: string | number
 * }, [key: string]: any }>} rules - The array of rules to transform.
 * @returns {Array<{ action: {
 *  [key: string]: string | number },
 *  [key: string]: any
 * }>} - The transformed rules array.
 */
export const transformActions = (rules) => rules.map((rule) => {
  if (rule.action && typeof rule.action === 'object') {
    const { eventType, count } = rule.action;
    return {
      ...rule,
      action: { [eventType]: count },
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
  rules: transformActions(removeTempIds(data.rules)),
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
 * Reverses the transformation applied by `transformActions`, converting the `action` object
 * back into `{ eventType, count }` format.
 *
 * @param {Array<{ action: { [key: string]: string | number },
* [key: string]: any }>} rules - The array of transformed rules.
* @returns {Array<{ action?: { eventType: string, count: string | number },
* [key: string]: any }>} - The restored rules array.
*/
export const reverseTransformActions = (rules) => rules.map((rule) => {
  if (rule.action && typeof rule.action === 'object') {
    const [eventType, count] = Object.entries(rule.action)[0] || [];
    return eventType
      ? { ...rule, action: { eventType, count } }
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
    rules: Array.isArray(avatar.rules) && avatar.rules.length > 0
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

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
    const { id, eventType, count } = rule.action;
    return {
      ...rule,
      action: { [eventType]: count },
      eventConfiguration: id ?? rule.eventConfiguration ?? null,
    };
  }
  return rule;
});

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
      ? { ...rule, action: { eventType, count }, eventConfiguration: rule.eventConfiguration ?? null }
      : rule;
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
 * Processes the received payload by restoring rule actions and adding temporary IDs if needed.
 *
 * @param {Object} data - The received payload data.
 * @param {Array} data.rules - The array of rules to process.
 * @returns {Object} - The processed payload with restored rules.
 */
export const processReceivedPayload = (data) => ({
  ...data,
  rules: Array.isArray(data.rules) && data.rules.length > 0
    ? reverseTransformActions(data.rules)
    : [],
});

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

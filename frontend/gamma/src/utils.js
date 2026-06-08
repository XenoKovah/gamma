/**
 * Retrieves the value of a cookie by its name.
 *
 * @param {string} cookieName - The name of the cookie to retrieve.
 * @returns {string|null} The value of the cookie if found, or `null` if the cookie does not exist.
 */
export const getCookieByName = (cookieName) => {
  const cookies = document.cookie.split('; ');
  for (const cookie of cookies) {
    const [name, value] = cookie.split('=');
    if (name === cookieName) {
      return decodeURIComponent(value);
    }
  }
  return null;
};

/**
 * Capitalizes the first letter of a string.
 * @param {string} str - Input string.
 * @returns {string} String with the first letter capitalized.
 */
export const capitalizeFirstLetter = (str = '') => str.charAt(0).toUpperCase() + str.slice(1);

/**
 * Returns a new array of strings sorted alphabetically.
 *
 * The sort is case-insensitive and numeric-aware (so e.g. "Dbg1016" sorts
 * before "Dbg2011"). The input array is not mutated.
 *
 * @param {string[]} [items=[]] - Input array of strings.
 * @returns {string[]} A new, alphabetically sorted array.
 */
export const sortAlphabetically = (items = []) => [...items].sort(
  (a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }),
);

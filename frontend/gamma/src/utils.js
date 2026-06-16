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

/**
 * Reads the header config the Django `GammaView` injects into the page via
 * `{{ gamma_header_config|json_script:"gamma-header-config" }}`.
 *
 * The standalone gamma React app only knows its own origin (the gamma host),
 * so the current user and the cross-host LMS/MFE base URLs + logo are supplied
 * by the backend. Returns `{}` if the element is missing or malformed (e.g. in
 * tests / local dev) so callers can fall back gracefully.
 *
 * @returns {{username?: string, name?: string, lmsBaseUrl?: string,
 *   mfeBaseUrl?: string, logoUrl?: string}} The parsed config, or `{}`.
 */
export const getGammaHeaderConfig = () => {
  try {
    const el = document.getElementById('gamma-header-config');
    return el ? JSON.parse(el.textContent) : {};
  } catch {
    return {};
  }
};

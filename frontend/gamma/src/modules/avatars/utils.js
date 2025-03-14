/**
 * Sets a timeout to automatically call the setter function with `false` after the specified delay.
 * Returns a cleanup function to clear the timeout if needed.
 *
 * @param {Function} setter - A state setter function that will be called with `false`.
 * @param {number} delay - The delay in milliseconds before the setter is triggered.
 * @returns {Function} A cleanup function that clears the timeout.
 */
export const setAutoClose = (setter, delay) => {
  const timer = setTimeout(() => setter(false), delay);
  return () => clearTimeout(timer);
};

/**
 * Sorts an array of objects by a date field.
 * @param {Array} array - The array to sort.
 * @param {string} key - The key of the date field.
 * @param {boolean} [desc=false] - Whether to sort in descending order.
 * @returns {Array} - The sorted array.
 */
export const sortByDate = (array, key, desc = false) => [...array].sort((a, b) => {
  const dateA = new Date(a[key]);
  const dateB = new Date(b[key]);
  return desc ? dateB - dateA : dateA - dateB;
});

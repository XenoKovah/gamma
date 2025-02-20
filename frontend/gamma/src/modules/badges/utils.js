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

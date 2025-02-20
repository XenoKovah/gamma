/**
 * Converts a given Date object to an ISO 8601 string in the format 'YYYY-MM-DDTHH:mm:ss'.
 *
 * @param {Date} date - The date object to be formatted.
 * @returns {string|null} The formatted date string in 'YYYY-MM-DDTHH:mm:ss' format, or null if the input is invalid.
 */
export const formatDateToISO = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }

  return date.toISOString().split('.')[0];
};

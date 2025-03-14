/**
 * Formats a Date object into an ISO 8601-like string in UTC without milliseconds.
 *
 * - Converts the provided Date object to a UTC-based timestamp.
 * - Uses `toISOString()` to generate a `YYYY-MM-DDTHH:MM:SS.sssZ` format.
 * - Removes milliseconds to match `YYYY-MM-DDTHH:MM:SS` format.
 *
 * @param {Date} date - The Date object to format.
 * @returns {string | null} The formatted date string in `YYYY-MM-DDTHH:MM:SS` format (UTC),
 * or `null` if the input is invalid.
 */
export const formatDateToISO = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }

  return new Date(Date.UTC(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
    date.getHours(),
    date.getMinutes(),
    date.getSeconds(),
  )).toISOString().slice(0, 19);
};

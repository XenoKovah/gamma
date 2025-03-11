/**
 * Formats a Date object into an ISO 8601-like string without timezone conversion.
 * - Uses the `sv-SE` (Swedish) locale to generate a `YYYY-MM-DD HH:MM:SS` format.
 * - Replaces the space with `T` to match `YYYY-MM-DDTHH:MM:SS` format.
 *
 * @param {Date} date - The Date object to format.
 * @returns {string | null} The formatted date string in `YYYY-MM-DDTHH:MM:SS` format,
 * or `null` if the input is invalid.
 */
export const formatDateToISO = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat('sv-SE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // 24-hour format
  }).format(date).replace(' ', 'T');
};

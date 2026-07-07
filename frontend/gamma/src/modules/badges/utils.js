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

// Group key used for badges that have no `category` set.
export const UNCATEGORIZED_KEY = '__uncategorized__';

/**
 * Group badges by their free-text `category` for the collapsible admin list.
 *
 * Badges keep their incoming order within each group (callers pass an
 * already-sorted list). Categories are ordered alphabetically, with the
 * "Uncategorized" bucket (badges with no category) always last.
 *
 * @param {Array<{category?: string}>} badges - Badges to group (pre-sorted).
 * @param {string} uncategorizedLabel - Localized label for the no-category bucket.
 * @returns {Array<{key: string, label: string, badges: Array<Object>}>} Ordered groups.
 */
export const groupBadgesByCategory = (badges = [], uncategorizedLabel = 'Uncategorized') => {
  const groups = new Map();

  badges.forEach((badge) => {
    const category = (badge.category || '').trim();
    const key = category || UNCATEGORIZED_KEY;
    if (!groups.has(key)) {
      groups.set(key, { key, label: category || uncategorizedLabel, badges: [] });
    }
    groups.get(key).badges.push(badge);
  });

  return Array.from(groups.values()).sort((a, b) => {
    if (a.key === UNCATEGORIZED_KEY) { return 1; }
    if (b.key === UNCATEGORIZED_KEY) { return -1; }
    return a.label.localeCompare(b.label, undefined, { sensitivity: 'base' });
  });
};

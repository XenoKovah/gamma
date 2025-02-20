/**
 * Dynamically imports all translation files from the `modules` directory.
 *
 * @constant {__WebpackModuleApi.RequireContext} modulesTranslations
 * - Webpack's `require.context` function that loads all translation files from `modules`.
 */
const modulesTranslations = require.context('../modules', true, /i18n\/\w+\.js$/);

/**
 * Dynamically imports all core translation files from the current directory.
 *
 * @constant {__WebpackModuleApi.RequireContext} coreTranslationsFiles
 * - Webpack's `require.context` function that loads all core translation files.
 */
const coreTranslationsFiles = require.context('./', false, /\.js$/);

/**
 * Converts a translation object into a format where the keys are the `id`
 * values, and the values are the corresponding `defaultMessage`.
 *
 * @param {Object} localeMessages - An object containing translation messages.
 * @returns {Object} An object where the keys are the message `id`s, and the values are `defaultMessage`s.
 */
const prepareMessages = (localeMessages) => Object.values(localeMessages).reduce((acc, message) => {
  acc[message.id] = message.defaultMessage;
  return acc;
}, {});

/**
 * Loads translations from core and module-specific translation files.
 *
 * @returns {Object} An object containing translations for different locales.
 * Each locale key (e.g., `en`, `uk`) maps to an object with translation messages.
 */
const loadTranslations = () => {
  const translations = {};

  coreTranslationsFiles.keys().forEach((filePath) => {
    const [, locale] = filePath.match(/(\w+)\.js$/) || [];

    if (locale) {
      const coreMessages = coreTranslationsFiles(filePath).default;
      translations[locale] = prepareMessages(coreMessages);
    }
  });

  modulesTranslations.keys().forEach((filePath) => {
    const [, locale] = filePath.match(/i18n\/(\w+)\.js$/) || [];

    if (locale) {
      const moduleMessages = modulesTranslations(filePath).default;
      translations[locale] = {
        ...translations[locale],
        ...prepareMessages(moduleMessages),
      };
    }
  });

  return translations;
};

/**
 * A global object containing loaded translations for all supported locales.
 *
 * @constant {Object} messages - An object where the keys are locale codes
 * (e.g., `en`, `uk`), and the values are objects containing translations.
 */
const messages = loadTranslations();

/**
 * Retrieves the translation messages for a given locale.
 *
 * @param {string} locale - The locale code (e.g., `en`, `uk`).
 * @returns {Object} The translation messages for the specified locale,
 * or the default (`en`) translations if the locale is not found.
 */
export const getMessages = (locale) => messages[locale] || messages.en;

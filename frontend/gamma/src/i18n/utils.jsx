import { useIntl } from 'react-intl';

/**
 * Dynamically requires all translations files from the `modules` directory.
 *
 * @constant {__WebpackModuleApi.RequireContext} requireModule
 * - Webpack's require.context function that loads all translation files.
 */
const modulesTranslations = require.context('../modules', true, /i18n\/\w+\.js$/);
const coreTranslations = require('./en').default;

/**
 * Prepares messages by extracting `defaultMessage` values from the provided locale messages.
 *
 * @param {Object} localeMessages - An object containing locale messages.
 * @returns {Object} An object mapping message keys to their `defaultMessage` values.
 */
const prepareMessages = (localeMessages) => Object.keys(localeMessages).reduce((acc, key) => {
  acc[key] = localeMessages[key].defaultMessage;
  return acc;
}, {});

/**
 * Loads and prepares translation messages from multiple files based on locale.
 *
 * @returns The `loadTranslations` function returns an object containing
 * translations for different locales. Each locale key in the object corresponds to
 * an object containing messages for that locale.
 */
const loadTranslations = () => {
  const translations = {};

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
 * A dictionary of prepared messages for supported locales.
 * Each locale maps to its corresponding default messages.
 */
const messages = loadTranslations();

/**
 * Retrieves the messages for a specified locale.
 *
 * @param {string} locale - The locale for which messages are requested.
 * @returns {Object} The messages for the given locale or fallback messages from `en.js`.
 */
export const getMessages = (locale) => messages[locale] || coreTranslations;

/**
 * A React Hook for translating messages using the `react-intl` library.
 *
 * @param {string} id - The ID of the message to translate.
 * @param {Object} [values={}] - An object of values to interpolate in the message.
 * @returns {string} The translated message.
 */
export const useTranslate = (id, values = {}) => {
  const intl = useIntl();
  const defaultMessage = messages.en?.[id]?.defaultMessage || coreTranslations[id]?.defaultMessage || '';
  return intl.formatMessage(
    { id, defaultMessage },
    values,
  );
};

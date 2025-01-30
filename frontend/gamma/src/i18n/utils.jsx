import { useIntl } from 'react-intl';

import en from './en';

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
 * A dictionary of prepared messages for supported locales.
 * Each locale maps to its corresponding default messages.
 */
const messages = {
  en: prepareMessages(en),
};

/**
 * Retrieves the messages for a specified locale.
 *
 * @param {string} locale - The locale for which messages are requested.
 * @returns {Object} The messages for the given locale or default messages if the locale is unsupported.
 */
export const getMessages = (locale) => messages[locale] || messages.en;

/**
 * A React Hook for translating messages using the `react-intl` library.
 *
 * @param {string} id - The ID of the message to translate.
 * @param {Object} [values={}] - An object of values to interpolate in the message.
 * @returns {string} The translated message.
 */
export const useTranslate = (id, values = {}) => {
  const intl = useIntl();
  const defaultMessage = en[id]?.defaultMessage || '';
  return intl.formatMessage(
    { id, defaultMessage },
    values,
  );
};

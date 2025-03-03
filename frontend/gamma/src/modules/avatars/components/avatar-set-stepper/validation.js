import * as Yup from 'yup';

/**
 * Returns a validation schema for the step title, including custom error messages and uniqueness validation.
 *
 * @param {Object} messages - An object containing validation error messages.
 * @param {string} messages.titleRequired - Error message when the title is required.
 * @param {string} messages.titleMaxLength - Error message when the title exceeds the maximum length.
 * @param {string} messages.titleLettersNumbers - Error message when the title contains invalid characters.
 * @param {string} messages.titleUnique - Error message when the title is not unique.
 * @param {Map<string, number>} avatarTitleMap - A map of existing avatar set titles (key: lowercase title, value: ID).
 * @returns {Yup.ObjectSchema} The validation schema for the step title.
 */
export const stepTitleValidationSchema = (messages, avatarTitleMap) => Yup.object({
  title: Yup.string()
    .required(messages.titleRequired)
    .max(50, messages.titleMaxLength)
    .matches(/^[a-zA-Z0-9\s]+$/, messages.titleLettersNumbers)
    .test(
      'non-empty-title',
      messages.titleRequired,
      (value) => value && value.trim().length > 0,
    )
    .test(
      'unique-title',
      messages.titleUnique,
      (value) => (value ? !avatarTitleMap.has(value.trim().toLowerCase()) : true),
    ),
});

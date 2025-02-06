import * as yup from 'yup';

/**
 * Returns a Yup validation schema for badge creation.
 *
 * @param {Object} messages - The validation messages for localization.
 * @param {string} messages.titleRequired - Error message when the title is missing.
 * @param {string} messages.slugRequired - Error message when the slug is missing.
 * @param {string} messages.slugInvalid - Error message when the slug format is incorrect.
 * @param {string} messages.descriptionRequired - Error message when the description is missing.
 * @param {string} messages.imageRequired - Error message when an image is not uploaded.
 * @param {string} messages.imageSize - Error message when an uploaded image exceeds the file size limit.
 * @returns {yup.ObjectSchema} The Yup validation schema for the form.
 */
export const getValidationSchema = (messages) => yup.object().shape({
  title: yup.string().required(messages.titleRequired),
  slug: yup
    .string()
    .matches(/^[a-zA-Z0-9_-]+$/, messages.slugInvalid)
    .required(messages.slugRequired),
  description: yup.string().required(messages.descriptionRequired),
  image: yup
    .mixed()
    .required(messages.imageRequired)
    .test('fileSize', messages.imageSize, (value) => value && value.size <= 2 * 1024 * 1024),
});

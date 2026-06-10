import * as yup from 'yup';

import { capitalizeFirstLetter } from '../../utils';
import { MAX_IMAGE_SIZE } from './constants';

// A block usage key, e.g. block-v1:OST2+Arch4001+2026+type@done+block@761ee26eb2ad...
const BLOCK_USAGE_KEY_PATTERN = /^block-v1:[^+\s]+\+[^+\s]+\+[^+\s]+\+type@[^+\s]+\+block@\S+$/;

/**
 * Returns a Yup validation schema for entity creation or updating.
 *
 * @param {Object} messages - The validation messages for localization.
 * @param {Object} messages.title - Title validation messages.
 * @param {string} messages.titleRequired - Error message when the title is missing.
 * @param {string} messages.titleMaxLength - Error message when the title exceeds the character limit.
 * @param {Object} messages.slug - Slug validation messages.
 * @param {string} messages.slug.slugRequired - Error message when the slug is missing.
 * @param {string} messages.slug.slugInvalid - Error message when the slug format is incorrect.
 * @param {string} messages.slug.slugMaxLength - Error message when the slug exceeds the character limit.
 * @param {Object} messages.description - Description validation messages.
 * @param {string} messages.descriptionRequired - Error message when the description is missing.
 * @param {string} messages.descriptionMaxLength - Error message when the description exceeds the character limit.
 * @param {Object} messages.image - Image validation messages.
 * @param {string} messages.image.imageRequired - Error message when an image is not uploaded.
 * @param {string} messages.image.imageSize - Error message when an uploaded image exceeds the file size limit.
 * @param {Object} messages.count - Count validation messages.
 * @param {string} messages.count.countRequired - Error message when the count is missing.
 * @param {string} messages.count.countPositive - Error message when the count is not positive.
 * @param {string} messages.count.countInt - Error message when the count is not an integer.
 * @param {string} messages.eventTypeRequired - Error message when the event type is missing.
 * @param {Object} entityData - The entity data, used to determine if slug validation should be applied.
 * @param {string} [entityData.slug] - The slug of the entity, if applicable.
 * @returns {yup.ObjectSchema} - The Yup validation schema for the form.
 */
export const getValidationSchema = (messages, entityData) => yup.object().shape({
  title: yup
    .string()
    // Any printable text is fine (the backend stores the title verbatim and
    // derives the slug via slugify); only control characters are rejected.
    .matches(/^[^\p{Cc}]+$/u, messages.titleInvalid)
    .required(messages.titleRequired)
    .max(100, messages.titleMaxLength),
  ...(Object.hasOwn(entityData, 'slug')
    ? {
      slug: yup
        .string()
        .matches(/^[a-zA-Z0-9_-]+$/, messages.slug.slugInvalid)
        .max(100, messages.slug.slugMaxLength),
    }
    : {}),
  ...(Object.hasOwn(entityData, 'points')
    ? {
      points: yup
        .number()
        .transform((value, originalValue) => (originalValue === '' ? 0 : value))
        .typeError(messages.points.pointsInt)
        .integer(messages.points.pointsInt)
        .min(0, messages.points.pointsPositive),
    }
    : {}),
  description: yup
    .string()
    .required(messages.descriptionRequired)
    .max(300, messages.descriptionMaxLength),
  image: yup
    .mixed()
    .required(messages.image.imageRequired)
    .test(
      'fileSize',
      messages.image.imageSize,
      (value) => typeof value === 'string' || (value instanceof File && value.size <= MAX_IMAGE_SIZE * 1024 * 1024), // 20MB
    ),

  rules: yup
    .array()
    .of(
      yup.object().shape({
        action: yup.object().shape({
          eventType: yup.string().required(messages.eventTypeRequired),
          id: yup.number().nullable(),
          count: yup.number().nullable(),
          points: yup.number().nullable(),
        })
          .test('action-value-required', messages.count.countRequired, (value) => {
            if (!value.eventType) {
              return true;
            }

            const hasValidCount = value.count != null && value.count !== '';
            const hasValidPoints = value.points != null && value.points !== '';

            return hasValidCount || hasValidPoints;
          })
          .test('action-value-positive', messages.count.countPositive, (value) => {
            if (!value.eventType) {
              return true;
            }

            const count = Number(value.count);
            const points = Number(value.points);

            const isCountValid = !value.count || count > 0;
            const isPointsValid = !value.points || points > 0;

            return isCountValid && isPointsValid;
          })
          .test('action-value-integer', messages.count.countInt, (value) => {
            if (!value.eventType) {
              return true;
            }

            const count = Number(value.count);
            const points = Number(value.points);

            const isCountInteger = !value.count || Number.isInteger(count);
            const isPointsInteger = !value.points || Number.isInteger(points);

            return isCountInteger && isPointsInteger;
          }),
        filters: yup.object(),
      }),
    )
    // Badges (entities with a points value) may be purely manual, so they can have
    // zero automatic rules. Other entities (avatars) still require at least one rule.
    .min(Object.hasOwn(entityData, 'points') ? 0 : 1),
});

/**
 * Validates filter rules and returns an object with errors.
 *
 * @param {Object} values - The object containing form values.
 * @param {Array} values.rules - An array of rule objects.
 * @param {Object} messages - An object containing validation messages.
 * @param {Object} messages.interval - Messages for interval validation.
 * @param {string} messages.interval.startDateRequired - Error message when the start date is missing.
 * @param {string} messages.interval.endDateRequired - Error message when the end date is missing.
 * @param {Object} messages.frequency - Messages for frequency validation.
 * @param {string} messages.frequency.frequencyInt - Error message when the frequency is not an integer.
 * @param {string} messages.frequency.frequencyPositiveInt - Error message when the frequency is not a positive integer.
 * @param {string} messages.filterKeyRequired - Error message when a required filter key is missing.
 * @returns {Object} An object containing validation errors,
 * structured as `{ rules: [...] }`, or an empty object if no errors.
 */
export const validateFilters = (values, messages) => {
  const errors = {};

  if (Array.isArray(values.rules)) {
    values.rules.forEach((rule, index) => {
      if (rule.filters && typeof rule.filters === 'object') {
        Object.entries(rule.filters).forEach(([filterKey, filterValue]) => {
          if (filterKey === 'interval' && typeof filterValue === 'object') {
            if (!filterValue.start) {
              if (!errors.rules) {
                errors.rules = [];
              }
              if (!errors.rules[index]) {
                errors.rules[index] = {
                  filters: {},
                };
              }
              if (!errors.rules[index].filters.interval) {
                errors.rules[index].filters.interval = {};
              }
              errors.rules[index].filters.interval.start = messages.interval.startDateRequired;
            }

            if (!filterValue.end) {
              if (!errors.rules) {
                errors.rules = [];
              }
              if (!errors.rules[index]) {
                errors.rules[index] = {
                  filters: {},
                };
              }
              if (!errors.rules[index].filters.interval) {
                errors.rules[index].filters.interval = {};
              }
              errors.rules[index].filters.interval.end = messages.interval.endDateRequired;
            }
          } else if (filterKey === 'frequency') {
            const parsedValue = Number(filterValue);
            if (Number.isNaN(parsedValue)) {
              if (!errors.rules) {
                errors.rules = [];
              }
              if (!errors.rules[index]) {
                errors.rules[index] = {
                  filters: {},
                };
              }
              errors.rules[index].filters.frequency = messages.frequency.frequencyInt;
            } else if (parsedValue <= 0) {
              if (!errors.rules) {
                errors.rules = [];
              }
              if (!errors.rules[index]) {
                errors.rules[index] = {
                  filters: {},
                };
              }
              errors.rules[index].filters.frequency = messages.frequency.frequencyPositiveInt;
            } else if (!Number.isInteger(parsedValue)) {
              if (!errors.rules) {
                errors.rules = [];
              }
              if (!errors.rules[index]) {
                errors.rules[index] = {
                  filters: {},
                };
              }
              errors.rules[index].filters.frequency = messages.frequency.frequencyInt;
            }
          } else if (
            filterKey === 'blocks'
            && Array.isArray(filterValue)
            && filterValue.length > 0
            && filterValue.some((block) => !BLOCK_USAGE_KEY_PATTERN.test(block))
          ) {
            if (!errors.rules) {
              errors.rules = [];
            }
            if (!errors.rules[index]) {
              errors.rules[index] = {
                filters: {},
              };
            }
            errors.rules[index].filters.blocks = 'Each block must be a usage id like block-v1:ORG+Course+Run+type@done+block@…';
          } else if (
            filterValue === undefined
            || filterValue === ''
            || (Array.isArray(filterValue) && filterValue.length === 0)
          ) {
            if (!errors.rules) {
              errors.rules = [];
            }
            if (!errors.rules[index]) {
              errors.rules[index] = {
                filters: {},
              };
            }
            errors.rules[index].filters[filterKey] = `${capitalizeFirstLetter(filterKey)} ${messages.filterKeyRequired}`;
          }
        });
      }
    });
  }

  return errors;
};

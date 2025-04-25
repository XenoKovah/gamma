import * as yup from 'yup';

import { capitalizeFirstLetter } from '../../utils';
import genericMessages from '../../i18n';
import { getValidationSchema, validateFilters } from './validation';
import { MAX_IMAGE_SIZE } from './constants';

describe('getValidationSchema', () => {
  const messages = {
    titleRequired: genericMessages.modalEntityValidationTitleRequiredText.defaultMessage,
    titleMaxLength: genericMessages.modalEntityValidationTitleMaxLengthText.defaultMessage,
    slug: {
      slugRequired: genericMessages.modalEntityValidationSlugRequiredText.defaultMessage,
      slugInvalid: genericMessages.modalEntityValidationSlugInvalidText.defaultMessage,
      slugMaxLength: genericMessages.modalEntityValidationSlugMaxLengthText.defaultMessage,
    },
    image: {
      imageRequired: genericMessages.modalEntityValidationImageRequiredText.defaultMessage,
      imageSize: genericMessages.modalEntityValidationImageSizeText.defaultMessage,
    },
    count: {
      countRequired: genericMessages.modalEntityValidationActionRequiredText.defaultMessage,
      countPositive: genericMessages.modalEntityValidationActionPositiveNumberText.defaultMessage,
      countInt: genericMessages.modalEntityValidationActionNumberText.defaultMessage,
    },
    descriptionRequired: genericMessages.modalEntityValidationDescriptionRequiredText.defaultMessage,
    descriptionMaxLength: genericMessages.modalEntityValidationDescriptionMaxLengthText.defaultMessage,
    eventTypeRequired: genericMessages.modalEntityValidationActionEventNameRequiredText.defaultMessage,
  };

  const validData = {
    title: 'Valid Title',
    slug: 'valid-slug',
    description: 'Valid description',
    image: new File([], 'image.png', { type: 'image/png' }),
    rules: [
      {
        action: {
          eventType: 'click',
          count: 5,
        },
      },
    ],
  };

  it('passes validation with correct data', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    await expect(schema.validate(validData)).resolves.toBeTruthy();
  });

  it('fails when required fields are missing', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    const invalidData = {
      title: '',
      slug: '',
      description: '',
      image: null,
      rules: [],
    };

    await expect(schema.validate(invalidData)).rejects.toThrow(yup.ValidationError);
  });

  it('fails when title exceeds character limit', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    const invalidData = { ...validData, title: 'A'.repeat(101) };

    await expect(schema.validate(invalidData)).rejects.toThrow(messages.titleMaxLength);
  });

  it('fails when slug format is invalid', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    const invalidData = { ...validData, slug: 'invalid slug!' };

    await expect(schema.validate(invalidData)).rejects.toThrow(messages.slug.slugInvalid);
  });

  it('fails when image is too large', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });
    const largeFileSize = MAX_IMAGE_SIZE + 1;

    const largeFile = new File([
      new Blob([new Uint8Array(largeFileSize * 1024 * 1024)]),
    ], 'large.png', { type: 'image/png' });

    const invalidData = { ...validData, image: largeFile };

    await expect(schema.validate(invalidData)).rejects.toThrow(messages.image.imageSize);
  });

  it('fails when count is not a positive integer', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    const invalidData = { ...validData, rules: [{ action: { eventType: 'click', count: -1 } }] };

    await expect(schema.validate(invalidData)).rejects.toThrow(messages.count.countPositive);
  });

  it('fails when eventType is missing', async () => {
    const schema = getValidationSchema(messages, { slug: 'valid-slug' });

    const invalidData = { ...validData, rules: [{ action: { count: 1 } }] };

    await expect(schema.validate(invalidData)).rejects.toThrow(messages.eventTypeRequired);
  });
});

describe('validateFilters', () => {
  const messages = {
    interval: {
      startDateRequired: genericMessages.modalEntityValidationStartDateRequiredText.defaultMessage,
      endDateRequired: genericMessages.modalEntityValidationEndDateRequiredText.defaultMessage,
    },
    frequency: {
      frequencyInt: genericMessages.modalEntityValidationFrequencyNumberText.defaultMessage,
      frequencyPositiveInt: genericMessages.modalEntityValidationFrequencyPositiveNumberText.defaultMessage,
    },
    filterKeyRequired: genericMessages.modalEntityValidationFiltersText.defaultMessage,
  };

  it('should return an empty object if there are no validation errors', () => {
    const validValues = {
      rules: [
        {
          filters: {
            interval: { start: '2024-05-15', end: '2024-05-20' },
            frequency: 10,
          },
        },
      ],
    };

    expect(validateFilters(validValues, messages)).toEqual({});
  });

  describe('should return an error if required fields are missing', () => {
    it('start date is missing', () => {
      const invalidValues = { rules: [{ filters: { interval: { end: '2024-05-20' } } }] };
      const expectedErrors = { rules: [{ filters: { interval: { start: messages.interval.startDateRequired } } }] };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });

    it('end date is missing', () => {
      const invalidValues = { rules: [{ filters: { interval: { start: '2024-05-15' } } }] };
      const expectedErrors = { rules: [{ filters: { interval: { end: messages.interval.endDateRequired } } }] };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });

    it('custom filter is empty', () => {
      const invalidValues = { rules: [{ filters: { customFilter: '' } }] };
      const expectedErrors = {
        rules: [{
          filters: { customFilter: `${capitalizeFirstLetter('customFilter')} ${messages.filterKeyRequired}` },
        }],
      };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });
  });

  describe('should return an error if frequency is invalid', () => {
    it('not a number', () => {
      const invalidValues = { rules: [{ filters: { frequency: 'not-a-number' } }] };
      const expectedErrors = { rules: [{ filters: { frequency: messages.frequency.frequencyInt } }] };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });

    it('not a positive integer', () => {
      const invalidValues = { rules: [{ filters: { frequency: -5 } }] };
      const expectedErrors = { rules: [{ filters: { frequency: messages.frequency.frequencyPositiveInt } }] };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });

    it('not an integer', () => {
      const invalidValues = { rules: [{ filters: { frequency: 3.14 } }] };
      const expectedErrors = { rules: [{ filters: { frequency: messages.frequency.frequencyInt } }] };

      expect(validateFilters(invalidValues, messages)).toEqual(expectedErrors);
    });
  });
});

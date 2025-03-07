import * as yup from 'yup';
import { getValidationSchema } from './validation';

import genericMessages from '../../i18n';

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
      countRequired: genericMessages.modalEntityValidationActionCountRequiredText.defaultMessage,
      countPositive: genericMessages.modalEntityValidationActionCountPositiveNumberText.defaultMessage,
      countInt: genericMessages.modalEntityValidationActionCountNumberText.defaultMessage,
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

    const largeFile = new File([new Blob([new Uint8Array(2.5 * 1024 * 1024)])], 'large.png', { type: 'image/png' });

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

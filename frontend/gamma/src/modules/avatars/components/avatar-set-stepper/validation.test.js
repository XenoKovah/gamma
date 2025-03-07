import moduleMessages from '../../i18n';
import { stepTitleValidationSchema } from './validation';

describe('stepTitleValidationSchema', () => {
  let translations;
  let avatarTitleMap;
  let schema;

  beforeEach(() => {
    translations = {
      validation: {
        titleStep: {
          titleRequired: moduleMessages.avatarSetStepperValidationTitleRequired,
          titleMaxLength: moduleMessages.avatarSetStepperValidationTitleMaxLength,
          titleLettersNumbers: moduleMessages.avatarSetStepperValidationTitleLettersNumbers,
          titleUnique: moduleMessages.avatarSetStepperValidationTitleUnique,
        },
      },
    };

    avatarTitleMap = new Map([
      ['existing title', 1],
      ['another title', 2],
    ]);

    schema = stepTitleValidationSchema(translations.validation.titleStep, avatarTitleMap);
  });

  it('should pass validation for a valid title', async () => {
    await expect(schema.validate({ title: 'Valid Title' })).resolves.toEqual({
      title: 'Valid Title',
    });
  });

  it('should fail validation when title is missing', async () => {
    await expect(schema.validate({}))
      .rejects.toThrow(translations.titleRequired);
  });

  it('should fail validation when title is empty or whitespace', async () => {
    await expect(schema.validate({ title: '   ' }))
      .rejects.toThrow(translations.titleRequired);
  });

  it('should fail validation when title exceeds 50 characters', async () => {
    const longTitle = 'A'.repeat(51);
    await expect(schema.validate({ title: longTitle }))
      .rejects.toThrow(translations.titleMaxLength);
  });

  it('should fail validation when title contains special characters', async () => {
    await expect(schema.validate({ title: 'Invalid@Title!' }))
      .rejects.toThrow(translations.titleLettersNumbers);
  });

  it('should fail validation when title is not unique', async () => {
    await expect(schema.validate({ title: 'Existing Title' }))
      .rejects.toThrow(translations.titleUnique);
  });

  it('should trim and convert title to lowercase for uniqueness check', async () => {
    await expect(schema.validate({ title: '  EXISTING TITLE  ' }))
      .rejects.toThrow(translations.titleUnique);
  });

  it('should allow titles that are not in the avatarTitleMap', async () => {
    await expect(schema.validate({ title: 'New Unique Title' })).resolves.toEqual({
      title: 'New Unique Title',
    });
  });
});

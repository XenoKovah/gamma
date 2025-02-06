import React from 'react';
import '@testing-library/jest-dom';
import { act, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Formik } from 'formik';

import { useTranslate } from '../../../../../i18n/utils';
import { getValidationSchema } from '../validation';
import { renderWithProviders } from '../../../../../setupTests';
import messages from '../../../i18n/en';
import BadgeInformation from '.';

jest.mock('../../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('BadgeInformation', () => {
  const translations = {
    titleRequired: messages['modules.badges.modal.validation.title.required'].defaultMessage,
    slugRequired: messages['modules.badges.modal.validation.slug.required'].defaultMessage,
    slugInvalid: messages['modules.badges.modal.validation.slug.invalid'].defaultMessage,
    descriptionRequired: messages['modules.badges.modal.validation.description.required'].defaultMessage,
    imageRequired: messages['modules.badges.modal.validation.image.required'].defaultMessage,
    imageSize: messages['modules.badges.modal.validation.image.size'].defaultMessage,
    'modules.badges.modal.badge.information.heading': messages['modules.badges.modal.badge.information.heading'].defaultMessage,
    'modules.badges.modal.badge.information.label.badge.title': messages['modules.badges.modal.badge.information.label.badge.title'].defaultMessage,
    'modules.badges.modal.badge.information.label.badge.slug': messages['modules.badges.modal.badge.information.label.badge.slug'].defaultMessage,
    'modules.badges.modal.badge.information.label.badge.description': messages['modules.badges.modal.badge.information.label.badge.description'].defaultMessage,
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  afterEach(cleanup);

  const validationSchema = getValidationSchema(translations);

  const renderComponent = (formikProps = {}) => renderWithProviders(
    <Formik
      initialValues={{
        title: '', slug: '', description: '', image: null,
      }}
      validationSchema={validationSchema}
      onSubmit={jest.fn()}
      {...formikProps}
    >
      <BadgeInformation />
    </Formik>,
  );

  it('renders BadgeInformation with correct labels', () => {
    const { getByRole, getByLabelText } = renderComponent();

    expect(getByRole('heading', { level: 2 })).toHaveTextContent(translations['modules.badges.modal.badge.information.heading']);
    expect(getByLabelText(translations['modules.badges.modal.badge.information.label.badge.title'])).toBeInTheDocument();
    expect(getByLabelText(translations['modules.badges.modal.badge.information.label.badge.slug'])).toBeInTheDocument();
    expect(getByLabelText(translations['modules.badges.modal.badge.information.label.badge.description'])).toBeInTheDocument();
  });

  it('updates input values when user types', async () => {
    const { findByDisplayValue, getByLabelText } = renderComponent();

    const titleInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.title']);
    const slugInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.slug']);
    const descriptionInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.description']);

    await act(async () => {
      await userEvent.clear(titleInput);
      await userEvent.type(titleInput, 'Test Title');
      await userEvent.clear(slugInput);
      await userEvent.type(slugInput, 'test-slug');
      await userEvent.clear(descriptionInput);
      await userEvent.type(descriptionInput, 'Test description');
    });

    await findByDisplayValue('Test Title');
    await findByDisplayValue('test-slug');
    await findByDisplayValue('Test description');

    expect(titleInput).toHaveValue('Test Title');
    expect(slugInput).toHaveValue('test-slug');
    expect(descriptionInput).toHaveValue('Test description');
  });

  it('displays validation errors when fields are touched and left empty', async () => {
    const { getByText, getByLabelText } = renderComponent({
      validateOnBlur: true,
      validateOnChange: false,
    });

    const titleInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.title']);
    const slugInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.slug']);
    const descriptionInput = getByLabelText(translations['modules.badges.modal.badge.information.label.badge.description']);

    await act(async () => {
      await userEvent.click(titleInput);
      await userEvent.tab();
      await userEvent.click(slugInput);
      await userEvent.tab();
      await userEvent.click(descriptionInput);
      await userEvent.tab();
    });

    expect(getByText(translations.titleRequired)).toBeInTheDocument();
    expect(getByText(translations.slugRequired)).toBeInTheDocument();
    expect(getByText(translations.descriptionRequired)).toBeInTheDocument();
  });
});

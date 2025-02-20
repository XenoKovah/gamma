import React from 'react';
import '@testing-library/jest-dom';
import { act, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Formik } from 'formik';

import { useTranslate } from '../../../i18n/utils';
import { getValidationSchema } from '../validation';
import { renderWithProviders } from '../../../setupTests';
import messages from '../../../i18n/en';
import EntityInfo from '.';

jest.mock('../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('EntityInfo', () => {
  const translations = {
    titleRequired: messages['generic.modal.entity.validation.title.required'].defaultMessage,
    descriptionRequired: messages['generic.modal.entity.validation.description.required'].defaultMessage,
    'generic.modal.entity.information.heading': messages['generic.modal.entity.information.heading'].defaultMessage,
    'generic.modal.entity.information.label.entity.title': messages['generic.modal.entity.information.label.entity.title'].defaultMessage,
    'generic.modal.entity.information.label.entity.slug': messages['generic.modal.entity.information.label.entity.slug'].defaultMessage,
    'generic.modal.entity.information.label.entity.description': messages['generic.modal.entity.information.label.entity.description'].defaultMessage,
    slug: {
      'generic.modal.entity.validation.slug.required': messages['generic.modal.entity.validation.slug.required'].defaultMessage,
      'generic.modal.entity.validation.slug.invalid': messages['generic.modal.entity.validation.slug.invalid'].defaultMessage,
    },
    image: {
      'generic.modal.entity.validation.image.required': messages['generic.modal.entity.validation.image.required'].defaultMessage,
      'generic.modal.entity.validation.image.size': messages['generic.modal.entity.validation.image.size'].defaultMessage,
    },
    count: {
      'generic.modal.entity.action.count.validation.required.text': messages['generic.modal.entity.action.count.validation.required.text'].defaultMessage,
      'generic.modal.entity.action.count.validation.positive-number.text': messages['generic.modal.entity.action.count.validation.positive-number.text'].defaultMessage,
      'generic.modal.entity.action.count.validation.int.text': messages['generic.modal.entity.action.count.validation.int.text'].defaultMessage,
    },
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
      <EntityInfo />
    </Formik>,
  );

  it('renders EntityInfo with correct labels', () => {
    const { getByRole, getByLabelText } = renderComponent();

    expect(getByRole('heading', { level: 2 })).toHaveTextContent(translations['generic.modal.entity.information.heading']);
    expect(getByLabelText(translations['generic.modal.entity.information.label.entity.title'])).toBeInTheDocument();
    expect(getByLabelText(translations['generic.modal.entity.information.label.entity.slug'])).toBeInTheDocument();
    expect(getByLabelText(translations['generic.modal.entity.information.label.entity.description'])).toBeInTheDocument();
  });

  it('updates input values when user types', async () => {
    const { findByDisplayValue, getByLabelText } = renderComponent();

    const titleInput = getByLabelText(translations['generic.modal.entity.information.label.entity.title']);
    const slugInput = getByLabelText(translations['generic.modal.entity.information.label.entity.slug']);
    const descriptionInput = getByLabelText(translations['generic.modal.entity.information.label.entity.description']);

    userEvent.clear(titleInput);

    userEvent.type(titleInput, 'Test Title');
    userEvent.clear(slugInput);

    userEvent.type(slugInput, 'test-slug');
    userEvent.clear(descriptionInput);

    userEvent.type(descriptionInput, 'Test description');

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

    const titleInput = getByLabelText(translations['generic.modal.entity.information.label.entity.title']);
    const slugInput = getByLabelText(translations['generic.modal.entity.information.label.entity.slug']);
    const descriptionInput = getByLabelText(translations['generic.modal.entity.information.label.entity.description']);

    await act(async () => {
      userEvent.click(titleInput);
      userEvent.tab();
      userEvent.click(slugInput);
      userEvent.tab();
      userEvent.click(descriptionInput);
      userEvent.tab();
    });

    waitFor(() => {
      expect(getByText(translations.titleRequired)).toBeInTheDocument();
      expect(getByText(translations.slug['generic.modal.entity.validation.slug.required'])).toBeInTheDocument();
      expect(getByText(translations.descriptionRequired)).toBeInTheDocument();
    });
  });
});

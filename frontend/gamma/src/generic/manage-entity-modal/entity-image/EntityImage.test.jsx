import React from 'react';
import { Formik } from 'formik';
import '@testing-library/jest-dom';
import { cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../setupTests';
import { useTranslate } from '../../../i18n/utils';
import { getValidationSchema } from '../validation';
import messages from '../../../i18n/en';
import EntityImage from '.';

jest.mock('../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('EntityImage', () => {
  const mockHandleImageUpload = jest.fn();

  const translations = {
    'generic.modal.entity.image.heading': messages['generic.modal.entity.image.heading'].defaultMessage,
    'generic.modal.entity.image.button.upload': messages['generic.modal.entity.image.button.upload'].defaultMessage,
    'generic.modal.entity.image.preview.screenReader.text': messages['generic.modal.entity.image.preview.screenReader.text'].defaultMessage,
    'generic.modal.entity.validation.image.required': messages['generic.modal.entity.validation.image.required'].defaultMessage,
    'generic.modal.entity.validation.image.size': messages['generic.modal.entity.validation.image.size'].defaultMessage,
    slug: {
      'generic.modal.entity.validation.slug.required': messages['generic.modal.entity.validation.slug.required'].defaultMessage,
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
    useTranslate.mockImplementation((key, values) => (key === 'modules.badges.total-badges.counter.text'
      ? translations[key].replace('{badgesCount}', values?.badgesCount || 0)
      : translations[key] || key));
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const validationSchema = getValidationSchema(translations);

  const renderComponent = (formikProps = {}, imagePreview = null) => renderWithProviders(
    <Formik
      initialValues={{ image: null }}
      validationSchema={validationSchema}
      onSubmit={jest.fn()}
      {...formikProps}
    >
      <EntityImage imagePreview={imagePreview} handleImageUpload={mockHandleImageUpload} />
    </Formik>,
  );

  it('renders EntityImage with upload button', () => {
    const { getByRole } = renderComponent();
    expect(getByRole('heading', { level: 2 })).toHaveTextContent(translations['generic.modal.entity.image.heading']);
    expect(getByRole('button', { name: translations['generic.modal.entity.image.button.upload'] })).toBeInTheDocument();
  });

  it('calls handleImageUpload when a valid file is selected', () => {
    const { getByLabelText } = renderComponent();
    const fileInput = getByLabelText(translations['generic.modal.entity.image.button.upload']);
    const validFile = new File(['dummy content'], 'entity.png', { type: 'image/png' });

    userEvent.upload(fileInput, validFile);

    expect(mockHandleImageUpload).toHaveBeenCalledTimes(1);
  });

  it('shows validation error when upload button is clicked without selecting a file', async () => {
    const { getByRole, getByText } = renderComponent();
    const uploadButton = getByRole('button', { name: translations['generic.modal.entity.image.button.upload'] });

    userEvent.click(uploadButton);

    await waitFor(() => {
      expect(getByText(translations['generic.modal.entity.validation.image.required'])).toBeInTheDocument();
    });
  });

  it('removes validation error after an image is uploaded', async () => {
    const {
      getByRole, getByText, getByLabelText, queryByText,
    } = renderComponent();
    const uploadButton = getByRole('button', { name: translations['generic.modal.entity.image.button.upload'] });
    const fileInput = getByLabelText(translations['generic.modal.entity.image.button.upload']);
    const validFile = new File(['dummy content'], 'entity.png', { type: 'image/png' });

    userEvent.click(uploadButton);

    await waitFor(() => {
      expect(getByText(translations['generic.modal.entity.validation.image.required'])).toBeInTheDocument();
    });

    userEvent.upload(fileInput, validFile);

    await waitFor(() => {
      expect(queryByText(translations['generic.modal.entity.validation.image.required'])).not.toBeInTheDocument();
    });
  });
});

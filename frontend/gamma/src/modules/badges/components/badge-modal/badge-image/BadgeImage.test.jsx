import React from 'react';
import { Formik } from 'formik';
import '@testing-library/jest-dom';
import {
  render, act, cleanup, waitFor,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { useTranslate } from '../../../../../i18n/utils';
import { getValidationSchema } from '../validation';
import messages from '../../../i18n/en';
import BadgeImage from '.';

jest.mock('../../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('BadgeImage', () => {
  const mockHandleImageUpload = jest.fn();

  const translations = {
    'modules.badges.modal.badge.image.heading': messages['modules.badges.modal.badge.image.heading'].defaultMessage,
    'modules.badges.modal.badge.image.button.upload': messages['modules.badges.modal.badge.image.button.upload'].defaultMessage,
    'modules.badges.modal.badge.image.preview.screenReader.text': messages['modules.badges.modal.badge.image.preview.screenReader.text'].defaultMessage,
    'modules.badges.modal.badge.image.preview.caption': messages['modules.badges.modal.badge.image.preview.caption'].defaultMessage,
    'modules.badges.modal.validation.image.required': messages['modules.badges.modal.validation.image.required'].defaultMessage,
    'modules.badges.modal.validation.image.size': messages['modules.badges.modal.validation.image.size'].defaultMessage,
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key) => translations[key] || key);
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const validationSchema = getValidationSchema(translations);

  const renderComponent = (formikProps = {}, imagePreview = null) => render(
    <Formik
      initialValues={{ image: null }}
      validationSchema={validationSchema}
      onSubmit={jest.fn()}
      {...formikProps}
    >
      <BadgeImage imagePreview={imagePreview} handleImageUpload={mockHandleImageUpload} />
    </Formik>,
  );

  it('renders BadgeImage with upload button', () => {
    const { getByRole } = renderComponent();
    expect(getByRole('heading', { level: 2 })).toHaveTextContent(translations['modules.badges.modal.badge.image.heading']);
    expect(getByRole('button', { name: translations['modules.badges.modal.badge.image.button.upload'] })).toBeInTheDocument();
  });

  it('calls handleImageUpload when a valid file is selected', async () => {
    const { getByLabelText } = renderComponent();
    const fileInput = getByLabelText(translations['modules.badges.modal.badge.image.button.upload']);
    const validFile = new File(['dummy content'], 'badge.png', { type: 'image/png' });

    await act(async () => {
      await userEvent.upload(fileInput, validFile);
    });

    expect(mockHandleImageUpload).toHaveBeenCalledTimes(1);
  });

  it('shows validation error when upload button is clicked without selecting a file', async () => {
    const { getByRole, getByText } = renderComponent();
    const uploadButton = getByRole('button', { name: translations['modules.badges.modal.badge.image.button.upload'] });

    await act(async () => {
      await userEvent.click(uploadButton);
    });

    await waitFor(() => {
      expect(getByText(translations['modules.badges.modal.validation.image.required'])).toBeInTheDocument();
    });
  });

  it('removes validation error after an image is uploaded', async () => {
    const {
      getByRole, getByText, getByLabelText, queryByText,
    } = renderComponent();
    const uploadButton = getByRole('button', { name: translations['modules.badges.modal.badge.image.button.upload'] });
    const fileInput = getByLabelText(translations['modules.badges.modal.badge.image.button.upload']);
    const validFile = new File(['dummy content'], 'badge.png', { type: 'image/png' });

    await act(async () => {
      await userEvent.click(uploadButton);
    });

    await waitFor(() => {
      expect(getByText(translations['modules.badges.modal.validation.image.required'])).toBeInTheDocument();
    });

    await act(async () => {
      await userEvent.upload(fileInput, validFile);
    });

    await waitFor(() => {
      expect(queryByText(translations['modules.badges.modal.validation.image.required'])).not.toBeInTheDocument();
    });
  });
});

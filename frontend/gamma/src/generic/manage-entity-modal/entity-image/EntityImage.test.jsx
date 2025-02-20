import React from 'react';
import { Formik } from 'formik';
import '@testing-library/jest-dom';
import { cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../setupTests';
import { getValidationSchema } from '../validation';
import messages from '../../../i18n';
import EntityImage from '.';

describe('EntityImage', () => {
  const mockHandleImageUpload = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const translations = {
    slug: {
      slugRequired: messages.modalEntityValidationSlugRequiredText.defaultMessage,
      slugInvalid: messages.modalEntityValidationSlugInvalidText.defaultMessage,
      slugMaxLength: messages.modalEntityValidationSlugMaxLengthText.defaultMessage,
    },
    image: {
      imageRequired: messages.modalEntityValidationImageRequiredText.defaultMessage,
      imageSize: messages.modalEntityValidationImageSizeText.defaultMessage,
    },
    count: {
      countRequired: messages.modalEntityValidationActionCountRequiredText.defaultMessage,
      countPositive: messages.modalEntityValidationActionCountPositiveNumberText.defaultMessage,
      countInt: messages.modalEntityValidationActionCountNumberText.defaultMessage,
    },
  };

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
    expect(getByRole('heading', { level: 2 }))
      .toHaveTextContent(messages.modalEntityImageHeadingText.defaultMessage);
    expect(
      getByRole('button', { name: messages.modalEntityImageBtnUploadText.defaultMessage }),
    ).toBeInTheDocument();
  });

  it('calls handleImageUpload when a valid file is selected', () => {
    const { getByLabelText } = renderComponent();
    const fileInput = getByLabelText(messages.modalEntityImageBtnUploadText.defaultMessage);
    const validFile = new File(['dummy content'], 'entity.png', { type: 'image/png' });

    userEvent.upload(fileInput, validFile);

    expect(mockHandleImageUpload).toHaveBeenCalledTimes(1);
  });

  it('shows validation error when upload button is clicked without selecting a file', async () => {
    const { getByRole, getByText } = renderComponent();
    const uploadButton = getByRole('button', {
      name: messages.modalEntityImageBtnUploadText.defaultMessage,
    });

    userEvent.click(uploadButton);

    await waitFor(() => {
      expect(
        getByText(messages.modalEntityValidationImageRequiredText.defaultMessage),
      ).toBeInTheDocument();
    });
  });

  it('removes validation error after an image is uploaded', async () => {
    const {
      getByRole, getByText, getByLabelText, queryByText,
    } = renderComponent();
    const uploadButton = getByRole('button', {
      name: messages.modalEntityImageBtnUploadText.defaultMessage,
    });
    const fileInput = getByLabelText(messages.modalEntityImageBtnUploadText.defaultMessage);
    const validFile = new File(['dummy content'], 'entity.png', { type: 'image/png' });

    userEvent.click(uploadButton);

    await waitFor(() => {
      expect(
        getByText(messages.modalEntityValidationImageRequiredText.defaultMessage),
      ).toBeInTheDocument();
    });

    userEvent.upload(fileInput, validFile);

    await waitFor(() => {
      expect(
        queryByText(messages.modalEntityValidationImageRequiredText.defaultMessage),
      ).not.toBeInTheDocument();
    });
  });
});

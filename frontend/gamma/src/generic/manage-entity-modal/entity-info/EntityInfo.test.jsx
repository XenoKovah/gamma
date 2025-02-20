import React from 'react';
import '@testing-library/jest-dom';
import { act, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Formik } from 'formik';

import { getValidationSchema } from '../validation';
import { renderWithProviders } from '../../../setupTests';
import messages from '../../../i18n';
import EntityInfo from '.';

describe('EntityInfo', () => {
  const translations = {
    titleRequired: messages.modalEntityValidationTitleRequiredText.defaultMessage,
    titleMaxLength: messages.modalEntityValidationTitleMaxLengthText.defaultMessage,
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
    descriptionRequired: messages.modalEntityValidationDescriptionRequiredText.defaultMessage,
    descriptionMaxLength: messages.modalEntityValidationDescriptionMaxLengthText.defaultMessage,
    eventTypeRequired: messages.modalEntityValidationActionEventNameRequiredText.defaultMessage,
  };

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

    expect(getByRole('heading', { level: 2 }))
      .toHaveTextContent(messages.modalEntityInfoHeadingText.defaultMessage);
    expect(getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(messages.modalEntityInfoLabelEntitySlugText.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage)).toBeInTheDocument();
  });

  it('updates input values when user types', async () => {
    const { findByDisplayValue, getByLabelText } = renderComponent();

    const titleInput = getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage);
    const slugInput = getByLabelText(messages.modalEntityInfoLabelEntitySlugText.defaultMessage);
    const descriptionInput = getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);

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

    const titleInput = getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage);
    const slugInput = getByLabelText(messages.modalEntityInfoLabelEntitySlugText.defaultMessage);
    const descriptionInput = getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);

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

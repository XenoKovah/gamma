import React from 'react';
import '@testing-library/jest-dom';
import { cleanup, waitFor } from '@testing-library/react';
import { Formik } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../setupTests';
import messages from '../../../i18n';
import { DEFAULT_FORM_VALUES } from '../constants';
import { getValidationSchema } from '../validation';
import FormInputController from './FormInputController';

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

const validationSchema = getValidationSchema(translations, DEFAULT_FORM_VALUES);

const renderComponent = (componentProps, formikProps = {}, initialValues = DEFAULT_FORM_VALUES) => renderWithProviders(
  <Formik
    initialValues={initialValues}
    validationSchema={validationSchema}
    onSubmit={jest.fn()}
    {...formikProps}
  >
    <FormInputController label="Test title" name="title" {...componentProps} />
  </Formik>,
);

describe('FormInputController', () => {
  afterEach(cleanup);

  it('renders input with label', async () => {
    const { getByLabelText } = renderComponent();
    await waitFor(() => getByLabelText('Test title'));
  });

  it('renders input with default props', async () => {
    const { getByLabelText } = renderComponent();
    const input = getByLabelText('Test title');

    await waitFor(() => {
      expect(input).toHaveAttribute('type', 'text');
      expect(input).toHaveAttribute('name', 'title');
    });
  });

  it('updates value when user types', async () => {
    const { getByLabelText } = renderComponent();
    const input = getByLabelText('Test title');

    userEvent.type(input, 'New Value');

    expect(input).toHaveValue('New Value');
  });

  it('shows validation error when input is invalid', async () => {
    const { getByText, getByLabelText } = renderComponent();

    userEvent.click(getByLabelText('Test title'));
    userEvent.tab();

    await waitFor(() => {
      expect(getByText(translations.titleRequired)).toBeInTheDocument();
    });
  });

  it('renders input inside Col when hasCol is true', () => {
    const { getByLabelText } = renderComponent();
    expect(getByLabelText('Test title').closest('.col')).toBeInTheDocument();
  });

  it('renders input without Col when hasCol is false', () => {
    const { getByLabelText } = renderComponent({ hasCol: false });

    expect(getByLabelText('Test title').closest('.col')).not.toBeInTheDocument();
  });
});

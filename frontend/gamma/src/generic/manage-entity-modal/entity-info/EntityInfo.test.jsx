import React from 'react';
import '@testing-library/jest-dom';
import { act, cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Formik } from 'formik';

import { getValidationSchema } from '../validation';
import { DEFAULT_FORM_VALUES } from '../constants';
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
      countRequired: messages.modalEntityValidationActionRequiredText.defaultMessage,
      countPositive: messages.modalEntityValidationActionPositiveNumberText.defaultMessage,
      countInt: messages.modalEntityValidationActionNumberText.defaultMessage,
    },
    descriptionRequired: messages.modalEntityValidationDescriptionRequiredText.defaultMessage,
    descriptionMaxLength: messages.modalEntityValidationDescriptionMaxLengthText.defaultMessage,
    eventTypeRequired: messages.modalEntityValidationActionEventNameRequiredText.defaultMessage,
  };

  afterEach(cleanup);

  const validationSchema = getValidationSchema(translations, DEFAULT_FORM_VALUES);

  const renderComponent = (initialValues = DEFAULT_FORM_VALUES, formikProps = {}) => renderWithProviders(
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={jest.fn()}
      {...formikProps}
    >
      <EntityInfo />
    </Formik>,
  );

  it('renders EntityInfo with correct labels', () => {
    const { getByRole, getByLabelText } = renderComponent();

    expect(getByRole('heading', { level: 3 }))
      .toHaveTextContent(messages.modalEntityInfoHeadingText.defaultMessage);
    expect(getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(messages.modalEntityInfoLabelEntityIsActiveText.defaultMessage)).toBeInTheDocument();
  });

  it('renders EntityInfo without slug label', () => {
    const { isActive, ...initialValuesWithoutSlug } = DEFAULT_FORM_VALUES;
    const { getByRole, getByLabelText, queryByLabelText } = renderComponent(initialValuesWithoutSlug);

    expect(getByRole('heading', { level: 3 }))
      .toHaveTextContent(messages.modalEntityInfoHeadingText.defaultMessage);
    expect(getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage)).toBeInTheDocument();
    expect(queryByLabelText(messages.modalEntityInfoLabelEntityIsActiveText.defaultMessage)).not.toBeInTheDocument();
  });

  it('updates input values when user types', async () => {
    const { findByDisplayValue, getByLabelText } = renderComponent();

    const titleInput = getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage);
    const descriptionInput = getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);

    userEvent.clear(titleInput);

    userEvent.type(titleInput, 'Test Title');

    userEvent.clear(descriptionInput);

    userEvent.type(descriptionInput, 'Test description');

    await findByDisplayValue('Test Title');
    await findByDisplayValue('Test description');

    expect(titleInput).toHaveValue('Test Title');
    expect(descriptionInput).toHaveValue('Test description');
  });

  it('displays validation errors when fields are touched and left empty', async () => {
    const { getByText, getByLabelText } = renderComponent(DEFAULT_FORM_VALUES, {
      validateOnBlur: true,
      validateOnChange: false,
    });

    const titleInput = getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage);
    const descriptionInput = getByLabelText(messages.modalEntityInfoLabelEntityDescriptionText.defaultMessage);

    await act(async () => {
      userEvent.click(titleInput);
      userEvent.tab();
      userEvent.tab();
      userEvent.click(descriptionInput);
      userEvent.tab();
    });

    await waitFor(() => {
      expect(getByText(translations.titleRequired)).toBeInTheDocument();
      expect(getByText(translations.descriptionRequired)).toBeInTheDocument();
    });
  });

  it('renders the Category field for badges (when category is in the form values)', async () => {
    const badgeValues = { ...DEFAULT_FORM_VALUES, category: '' };
    const { getByLabelText, findByDisplayValue } = renderComponent(badgeValues);

    const categoryInput = getByLabelText(messages.modalEntityInfoLabelEntityCategoryText.defaultMessage);
    expect(categoryInput).toBeInTheDocument();

    userEvent.type(categoryInput, 'Security');
    await findByDisplayValue('Security');
    expect(categoryInput).toHaveValue('Security');
  });

  it('prefills the Category field from existing badge data on edit', () => {
    const badgeValues = { ...DEFAULT_FORM_VALUES, category: 'Reverse Engineering' };
    const { getByLabelText } = renderComponent(badgeValues);

    expect(getByLabelText(messages.modalEntityInfoLabelEntityCategoryText.defaultMessage))
      .toHaveValue('Reverse Engineering');
  });

  it('does not render the Category field for non-badge entities (no category key)', () => {
    const { queryByLabelText } = renderComponent();

    expect(queryByLabelText(messages.modalEntityInfoLabelEntityCategoryText.defaultMessage))
      .not.toBeInTheDocument();
  });

  it('trims leading and trailing spaces from title on blur', async () => {
    const { getByLabelText } = renderComponent(DEFAULT_FORM_VALUES, {
      validateOnBlur: false,
      validateOnChange: false,
    });

    const titleInput = getByLabelText(messages.modalEntityInfoLabelEntityTitle.defaultMessage);

    userEvent.clear(titleInput);
    userEvent.type(titleInput, '  Test Title  ');

    userEvent.tab();

    await waitFor(() => {
      expect(titleInput).toHaveValue('Test Title');
    });
  });
});

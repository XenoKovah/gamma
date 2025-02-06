import React from 'react';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import { useTranslate } from '../../i18n/utils';
import messages from '../../i18n/en';
import Modal from '.';

jest.mock('../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('Modal and ModalFooter Components', () => {
  const mockHandleClose = jest.fn();
  const mockSubmitFn = jest.fn();

  const defaultProps = {
    title: 'Delete Item',
    isOpen: true,
    handleClose: mockHandleClose,
    children: 'Are you sure you want to delete this item?',
    submitBtnOptions: {
      title: 'Confirm',
      submitFn: mockSubmitFn,
      disabled: false,
    },
  };

  const translations = {
    'generic.modal.dialog.button.cancel.text': messages['generic.modal.dialog.button.cancel.text'].defaultMessage,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  afterEach(() => {
    jest.clearAllMocks();
    cleanup();
  });

  const renderComponent = (props = {}) => renderWithProviders(<Modal {...defaultProps} {...props} />);

  it('renders Modal with title and content', () => {
    const { getByText } = renderComponent();

    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByText(defaultProps.children)).toBeInTheDocument();
  });

  it('calls handleClose when close button is clicked', () => {
    const { getByRole } = renderComponent({ hasCloseButton: true });

    const closeButton = getByRole('button', { name: translations['generic.modal.dialog.button.cancel.text'] });
    userEvent.click(closeButton);

    expect(mockHandleClose).toHaveBeenCalledTimes(1);
  });

  it('calls submit function when submit button is clicked', () => {
    const { getByRole } = renderComponent();

    const submitButton = getByRole('button', { name: defaultProps.submitBtnOptions.title });
    userEvent.click(submitButton);

    expect(mockSubmitFn).toHaveBeenCalledTimes(1);
  });

  it('disables submit button when submitBtnOptions.disabled is true', () => {
    const { getByRole } = renderComponent({
      submitBtnOptions: { ...defaultProps.submitBtnOptions, disabled: true },
    });

    expect(getByRole('button', { name: defaultProps.submitBtnOptions.title })).toBeDisabled();
  });

  it('does not render Modal when isOpen is false', () => {
    const { queryByText } = renderComponent({ isOpen: false });

    expect(queryByText(defaultProps.title)).not.toBeInTheDocument();
  });
});

import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n';
import { submitBtnStatuses } from '../status-button';
import Modal from '.';

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

  beforeEach(() => {
    jest.clearAllMocks();
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

    const closeButton = getByRole('button', { name: messages.modalDialogBtnCancelText.defaultMessage });
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

  it('renders StatusButton when isStatefulButton is true', () => {
    const { getByTestId } = renderComponent({
      submitBtnOptions: {
        title: messages.modalDialogBtnSubmitText.defaultMessage,
        submitFn: mockSubmitFn,
        disabled: false,
        isStatefulButton: true,
        submitStatus: submitBtnStatuses.PENDING,
      },
    });

    expect(getByTestId('status-button')).toBeInTheDocument();
  });

  it('passes correct props to StatusButton', () => {
    const { getByTestId } = renderComponent({
      submitBtnOptions: {
        submitFn: mockSubmitFn,
        disabled: false,
        isStatefulButton: true,
        submitStatus: submitBtnStatuses.ERROR,
      },
    });

    const statusButton = getByTestId('status-button');
    expect(statusButton).toHaveClass('btn-danger');
    expect(statusButton).toHaveTextContent(messages.modalDialogBtnStatefulErrorText.defaultMessage);
  });

  it('StatusButton is disabled when submitBtnOptions.disabled is true', () => {
    const { getByTestId } = renderComponent({
      submitBtnOptions: {
        submitFn: mockSubmitFn,
        disabled: true,
        isStatefulButton: true,
        submitStatus: submitBtnStatuses.DEFAULT,
      },
    });

    waitFor(() => {
      expect(getByTestId('status-button')).toBeDisabled();
    });
  });
});

import React from 'react';
import '@testing-library/jest-dom/extend-expect';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n';
import AlertModal from '.';

describe('AlertModal', () => {
  const mockOnClose = jest.fn();
  const mockOnDelete = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
    cleanup();
  });

  const defaultProps = {
    title: 'Alert Modal Title',
    isOpen: true,
    onClose: mockOnClose,
    onDelete: mockOnDelete,
    description: 'Alert Modal Description',
  };

  const renderComponent = (props = {}) => renderWithProviders(<AlertModal {...defaultProps} {...props} />);

  it('renders AlertModal with correct title and description', () => {
    const { getByText } = renderComponent();

    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByText(defaultProps.description)).toBeInTheDocument();
  });

  it('calls onClose when Cancel button is clicked', () => {
    const { getByRole } = renderComponent();

    const cancelButton = getByRole('button', { name: messages.alertBtnCancelText.defaultMessage });
    userEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onDelete when Delete button is clicked', () => {
    const { getByRole } = renderComponent();

    const deleteButton = getByRole('button', { name: messages.alertBtnDeleteText.defaultMessage });
    userEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledTimes(1);
  });

  it('does not render when isOpen is false', () => {
    const { queryByText } = renderComponent({ isOpen: false });

    expect(queryByText(defaultProps.title)).not.toBeInTheDocument();
  });

  it('renders with a different title and description when props are changed', () => {
    const newTitleAndDescription = {
      title: 'New Alert Modal Title',
      description: 'New alert modal description',
    };
    const { getByText } = renderComponent(newTitleAndDescription);

    expect(getByText(newTitleAndDescription.title)).toBeInTheDocument();
    expect(getByText(newTitleAndDescription.title)).toBeInTheDocument();
  });
});

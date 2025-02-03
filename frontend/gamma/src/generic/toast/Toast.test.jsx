import React from 'react';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n/en';
import ToastComponent from '.';

describe('ToastComponent', () => {
  afterEach(cleanup);

  const defaultProps = {
    text: messages['generic.toast.error.text'].defaultMessage,
    variant: 'danger',
    isShow: true,
    onClose: jest.fn(),
  };

  const renderComponent = (props = {}) => renderWithProviders(<ToastComponent {...defaultProps} {...props} />);

  it('renders the toast with the correct text', () => {
    const { getByText } = renderComponent();
    expect(getByText(messages['generic.toast.error.text'].defaultMessage)).toBeInTheDocument();
  });

  it('renders the toast with the correct variant class', () => {
    renderComponent();
    // Searching by role is avoided due to duplicated roles in Paragon's portal wrapper.
    // Paragon issue: https://github.com/openedx/paragon/issues/3409
    const toast = document.querySelector('.toast-component');
    expect(toast).toBeInTheDocument();
    expect(toast).toHaveClass('toast-danger');
  });

  it('calls onClose when the close button is clicked', () => {
    const { getByRole } = renderComponent();
    const closeButton = getByRole('button', { name: /close/i });
    userEvent.click(closeButton);

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('does not render when show is false', () => {
    renderComponent({ isShow: false });
    // Searching by role is avoided due to duplicated roles in Paragon's portal wrapper.
    // Paragon issue: https://github.com/openedx/paragon/issues/3409
    const toast = document.querySelector('.toast-component');
    expect(toast).not.toBeInTheDocument();
  });
});

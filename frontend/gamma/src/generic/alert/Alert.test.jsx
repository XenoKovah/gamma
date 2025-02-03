import React from 'react';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n/en';
import AlertComponent from '.';

describe('AlertComponent', () => {
  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <AlertComponent
      variant="success"
      title={messages['generic.alert.success.title'].defaultMessage}
      description={messages['generic.alert.success.description'].defaultMessage}
      {...props}
    />,
  );

  it('renders the alert with the correct title and description', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('alert')).toBeInTheDocument();
    expect(getByText(messages['generic.alert.success.title'].defaultMessage)).toBeInTheDocument();
    expect(getByText(messages['generic.alert.success.description'].defaultMessage)).toBeInTheDocument();
  });

  it('calls onClose when the close button is clicked', () => {
    const onCloseMock = jest.fn();
    const { getByRole } = renderComponent({
      variant: 'danger',
      title: messages['generic.alert.danger.title'].defaultMessage,
      description: messages['generic.alert.danger.description'].defaultMessage,
      onClose: onCloseMock,
    });

    const closeButton = getByRole('button', { name: /dismiss/i });
    userEvent.click(closeButton);

    expect(onCloseMock).toHaveBeenCalledTimes(1);
  });

  it('renders with the correct variant class', () => {
    const { container } = renderComponent({
      variant: 'warning',
      title: 'Warning Title',
      description: 'Warning Description',
    });

    expect(container.querySelector('.alert-warning')).toBeInTheDocument();
  });
});

import React from 'react';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n';
import AlertComponent from '.';

describe('AlertComponent', () => {
  afterEach(cleanup);
  const alertTitle = 'Successfully saved';
  const alertDescription = 'Your changes have been successfully saved.';

  const renderComponent = (props = {}) => renderWithProviders(
    <AlertComponent
      variant="success"
      title={alertTitle}
      description={alertDescription}
      isDismissible
      {...props}
    />,
  );

  it('renders the alert with the correct title and description', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('alert')).toBeInTheDocument();
    expect(getByText(alertTitle)).toBeInTheDocument();
    expect(getByText(alertDescription)).toBeInTheDocument();
  });

  it('calls onClose when the close button is clicked', () => {
    const onCloseMock = jest.fn();
    const { getByRole } = renderComponent({
      variant: 'danger',
      title: messages.alertDangerTitle.defaultMessage,
      description: messages.alertDangerDescription.defaultMessage,
      onClose: onCloseMock,
      isDismissible: true,
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

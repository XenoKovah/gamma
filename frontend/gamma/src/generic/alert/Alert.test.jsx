import React from 'react';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/extend-expect';

import { renderWithProviders } from '../../setupTests';
import { useTranslate } from '../../i18n/utils';
import messages from '../../i18n/en';
import AlertComponent from '.';

jest.mock('../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('AlertComponent', () => {
  afterEach(cleanup);

  const translations = {
    'generic.alert.success.title': messages['generic.alert.success.title'].defaultMessage,
    'generic.alert.success.description': messages['generic.alert.success.description'].defaultMessage,
    'generic.alert.danger.title': messages['generic.alert.danger.title'].defaultMessage,
    'generic.alert.danger.description': messages['generic.alert.danger.description'].defaultMessage,
    'generic.alert.button.close.title': messages['generic.alert.button.close.title'].defaultMessage,
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  const renderComponent = (props = {}) => renderWithProviders(
    <AlertComponent
      variant="success"
      title={translations['generic.alert.success.title']}
      description={translations['generic.alert.success.description']}
      isDismissible
      {...props}
    />,
  );

  it('renders the alert with the correct title and description', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('alert')).toBeInTheDocument();
    expect(getByText(translations['generic.alert.success.title'])).toBeInTheDocument();
    expect(getByText(translations['generic.alert.success.description'])).toBeInTheDocument();
  });

  it('calls onClose when the close button is clicked', () => {
    const onCloseMock = jest.fn();
    const { getByRole } = renderComponent({
      variant: 'danger',
      title: useTranslate('generic.alert.danger.title'),
      description: useTranslate('generic.alert.danger.description'),
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

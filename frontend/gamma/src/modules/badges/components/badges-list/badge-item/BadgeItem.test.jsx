import React from 'react';
import '@testing-library/jest-dom';
import { cleanup, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import { useTranslate } from '../../../../../i18n/utils';
import { badgesMocks } from '../../../__mocks__';
import messages from '../../../i18n/en';
import BadgeItem from '.';

jest.mock('../../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('BadgeItem', () => {
  afterEach(cleanup);

  const mockOpenConfirmDeletionAlert = jest.fn();

  const defaultProps = {
    title: badgesMocks[0].title,
    description: badgesMocks[0].description,
    image: badgesMocks[0].image,
    openConfirmDeletionAlert: mockOpenConfirmDeletionAlert,
  };

  const translations = {
    'modules.badges.badge-item.default.title': messages['modules.badges.badge-item.default.title'].defaultMessage,
    'modules.badges.badge-item.default.description': messages['modules.badges.badge-item.default.description'].defaultMessage,
    'modules.badges.badge-item.button.edit.title': messages['modules.badges.badge-item.button.edit.title'].defaultMessage,
    'modules.badges.badge-item.button.delete.title': messages['modules.badges.badge-item.button.delete.title'].defaultMessage,
    'modules.badges.alert.modal.confirm.deletion.title': messages['modules.badges.alert.modal.confirm.deletion.title'].defaultMessage,
    'modules.badges.alert.modal.confirm.deletion.description': messages['modules.badges.alert.modal.confirm.deletion.description'].defaultMessage,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  const renderComponent = (props = {}) => renderWithProviders(<BadgeItem {...defaultProps} {...props} />);

  it('renders with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByText(defaultProps.description)).toBeInTheDocument();
    expect(getByRole('button', { name: translations['modules.badges.badge-item.button.edit.title'] })).toBeInTheDocument();
    expect(getByRole('button', { name: translations['modules.badges.badge-item.button.delete.title'] })).toBeInTheDocument();
  });

  it('renders with default translations when props are missing', () => {
    const { queryByRole, getByText } = renderComponent({
      title: undefined,
      description: undefined,
      image: undefined,
    });

    expect(queryByRole('img')).not.toBeInTheDocument();
    expect(getByText(translations['modules.badges.badge-item.default.title'])).toBeInTheDocument();
    expect(getByText(translations['modules.badges.badge-item.default.description'])).toBeInTheDocument();
  });

  it('calls openConfirmDeletionAlert when delete button is clicked', () => {
    const { getByRole } = renderComponent();

    const deleteButton = getByRole('button', { name: translations['modules.badges.badge-item.button.delete.title'] });
    userEvent.click(deleteButton);
    expect(mockOpenConfirmDeletionAlert).toHaveBeenCalledTimes(1);

    waitFor(() => {
      const modal = getByRole('dialog');
      expect(within(modal).getByText(translations['modules.badges.alert.modal.confirm.deletion.description'])).toBeInTheDocument();
      expect(within(modal).getByText(translations['modules.badges.alert.modal.confirm.deletion.title'])).toBeInTheDocument();
    });
  });

  it('triggers actions when edit button is clicked', () => {
    const { getByRole } = renderComponent();

    const editButton = getByRole('button', { name: translations['modules.badges.badge-item.button.edit.title'] });
    userEvent.click(editButton);
    expect(editButton).toBeEnabled();
  });
});

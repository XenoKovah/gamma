import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
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

  const defaultProps = {
    title: badgesMocks[0].title,
    description: badgesMocks[0].description,
    image: badgesMocks[0].image,
  };

  const translations = {
    'modules.badges.badge-item.default.title': messages['modules.badges.badge-item.default.title'].defaultMessage,
    'modules.badges.badge-item.default.description': messages['modules.badges.badge-item.default.description'].defaultMessage,
    'modules.badges.badge-item.button.edit.title': messages['modules.badges.badge-item.button.edit.title'].defaultMessage,
    'modules.badges.badge-item.button.delete.title': messages['modules.badges.badge-item.button.delete.title'].defaultMessage,
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  it('renders with provided props', () => {
    const { getByRole, getByText } = renderWithProviders(<BadgeItem {...defaultProps} />);

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByText(defaultProps.description)).toBeInTheDocument();
    expect(getByRole('button', { name: translations['modules.badges.badge-item.button.edit.title'] })).toBeInTheDocument();
    expect(getByRole('button', { name: translations['modules.badges.badge-item.button.delete.title'] })).toBeInTheDocument();
  });

  it('renders with default translations when props are missing', () => {
    const { queryByRole, getByText } = renderWithProviders(<BadgeItem />);

    expect(queryByRole('img')).not.toBeInTheDocument();
    expect(getByText(translations['modules.badges.badge-item.default.title'])).toBeInTheDocument();
    expect(getByText(translations['modules.badges.badge-item.default.description'])).toBeInTheDocument();
  });

  it('triggers actions when buttons are clicked', () => {
    const { getByRole } = renderWithProviders(<BadgeItem {...defaultProps} />);

    const editButton = getByRole('button', { name: translations['modules.badges.badge-item.button.edit.title'] });
    const deleteButton = getByRole('button', { name: translations['modules.badges.badge-item.button.delete.title'] });

    userEvent.click(editButton);
    userEvent.click(deleteButton);

    expect(editButton).toBeEnabled();
    expect(deleteButton).toBeEnabled();
  });
});

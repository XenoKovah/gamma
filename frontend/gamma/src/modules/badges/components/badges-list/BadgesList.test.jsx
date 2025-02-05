import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../../../setupTests';
import { useTranslate } from '../../../../i18n/utils';
import { badgesMocks } from '../../__mocks__';
import messages from '../../i18n/en';
import BadgesList from '.';

jest.mock('../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('BadgesList', () => {
  afterEach(cleanup);

  const translations = {
    'modules.badges.badge-item.default.title': messages['modules.badges.badge-item.default.title'].defaultMessage,
    'modules.badges.badge-item.default.description': messages['modules.badges.badge-item.default.description'].defaultMessage,
    'modules.badges.badge-item.button.edit.title': messages['modules.badges.badge-item.button.edit.title'].defaultMessage,
    'modules.badges.badge-item.button.delete.title': messages['modules.badges.badge-item.button.delete.title'].defaultMessage,
    'modules.badges.alert.empty-badges-list.title': 'No badges available',
    'modules.badges.alert.empty-badges-list.description': 'There are currently no badges to display.',
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  it('renders a list of badges with provided data', () => {
    const { getByText, getByRole } = renderWithProviders(<BadgesList badgesData={badgesMocks} />);

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
      expect(getByRole('img', { name: badge.title })).toBeInTheDocument();
    });
  });

  it('renders badges with default values when props are missing', () => {
    const badgesWithMissingProps = [{
      id: 1, title: '', description: '', image: '',
    }];
    const { getByText } = renderWithProviders(<BadgesList badgesData={badgesWithMissingProps} />);

    expect(getByText(translations['modules.badges.badge-item.default.title'])).toBeInTheDocument();
    expect(getByText(translations['modules.badges.badge-item.default.description'])).toBeInTheDocument();
  });

  it('renders an alert when no badges are provided', () => {
    const { getByText } = renderWithProviders(<BadgesList badgesData={[]} />);

    expect(getByText(translations['modules.badges.alert.empty-badges-list.title'])).toBeInTheDocument();
    expect(getByText(translations['modules.badges.alert.empty-badges-list.description'])).toBeInTheDocument();
  });
});

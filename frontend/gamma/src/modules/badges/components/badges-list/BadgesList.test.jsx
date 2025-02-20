import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../../../setupTests';
import { badgesMocks } from '../../__mocks__';
import messages from '../../i18n';
import BadgesList from '.';

describe('BadgesList', () => {
  afterEach(cleanup);

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

    expect(getByText(messages.badgeDefaultTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.badgeDefaultDescription.defaultMessage)).toBeInTheDocument();
  });

  it('renders an alert when no badges are provided', () => {
    const { getByText } = renderWithProviders(<BadgesList badgesData={[]} />);

    expect(getByText(messages.alertEmptyBadgesListTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.alertEmptyBadgesListDescription.defaultMessage)).toBeInTheDocument();
  });
});

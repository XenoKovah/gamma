import React from 'react';
import '@testing-library/jest-dom';
import { cleanup, fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../../../setupTests';
import { badgesMocks } from '../../__mocks__';
import messages from '../../i18n';
import BadgesList from '.';

describe('BadgesList', () => {
  afterEach(cleanup);

  it('groups badges by category, collapsed by default, and reveals them on expand', () => {
    const {
      getByText, queryByText, getByRole,
    } = renderWithProviders(<BadgesList badgesData={badgesMocks} />);

    // The mock badges have no category, so they live under one "Uncategorized"
    // group whose header is shown while the badges stay collapsed (unmounted).
    const header = getByText(messages.badgesUncategorizedLabel.defaultMessage);
    expect(header).toBeInTheDocument();
    expect(queryByText(badgesMocks[0].title)).not.toBeInTheDocument();

    fireEvent.click(header);

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
      expect(getByRole('img', { name: badge.title })).toBeInTheDocument();
    });
  });

  it('renders one collapsible group per category (Uncategorized last)', () => {
    const badgesData = [
      {
        id: 1, title: 'Community One', description: 'd', category: 'Community', createdAt: '2025-01-01',
      },
      {
        id: 2, title: 'No category', description: 'd', category: '', createdAt: '2025-01-02',
      },
    ];
    const { getByText } = renderWithProviders(<BadgesList badgesData={badgesData} />);

    expect(getByText('Community')).toBeInTheDocument();
    expect(getByText(messages.badgesUncategorizedLabel.defaultMessage)).toBeInTheDocument();
  });

  it('renders badge default values when props are missing (after expanding)', () => {
    const badgesWithMissingProps = [{
      id: 1, title: '', description: '', image: '',
    }];
    const { getByText } = renderWithProviders(<BadgesList badgesData={badgesWithMissingProps} />);

    fireEvent.click(getByText(messages.badgesUncategorizedLabel.defaultMessage));

    expect(getByText(messages.badgeDefaultTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.badgeDefaultDescription.defaultMessage)).toBeInTheDocument();
  });

  it('renders an alert when no badges are provided', () => {
    const { getByText } = renderWithProviders(<BadgesList badgesData={[]} />);

    expect(getByText(messages.alertEmptyBadgesListTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.alertEmptyBadgesListDescription.defaultMessage)).toBeInTheDocument();
  });
});

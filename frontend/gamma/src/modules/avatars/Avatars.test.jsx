import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../setupTests';
import moduleMessages from './i18n';
import { Avatars } from '.';

describe('Avatars Component', () => {
  afterEach(cleanup);

  it('renders the footer on the page', async () => {
    const { getByRole } = renderWithProviders(<Avatars />);

    const footer = getByRole('contentinfo');
    expect(footer).toBeInTheDocument();
  });

  it('displays the correct page heading', async () => {
    const { getByRole } = renderWithProviders(<Avatars />);

    const heading = getByRole('heading', {
      level: 1, name: moduleMessages.pageTitle.defaultMessage,
    });
    expect(heading).toBeInTheDocument();
  });

  it('renders an empty avatars list message', async () => {
    const { getByText } = renderWithProviders(<Avatars />);

    expect(getByText(moduleMessages.alertEmptyAvatarsListTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(moduleMessages.alertEmptyAvatarsListDescription.defaultMessage)).toBeInTheDocument();
  });

  it('correctly displays the total number of badges on the page', async () => {
    const { getByText } = renderWithProviders(<Avatars />);

    expect(getByText(
      moduleMessages.totalAvatarsCount.defaultMessage.replace('{avatarsCount}', 0),
    )).toBeInTheDocument();
  });
});

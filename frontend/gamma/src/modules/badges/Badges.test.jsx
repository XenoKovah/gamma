import React from 'react';
import axios from 'axios';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../setupTests';
import genericMessages from '../../i18n';
import { submitBtnStatuses } from '../../generic/status-button';
import { useBadges } from './hooks/useBadges';
import { convertKeysToSnakeCase } from './data/utils';
import moduleMessages from './i18n';
import { fetchBadgesData, API_ROUTES } from './data';
import { Badges } from '.';

import { badgesMocks } from './__mocks__';

jest.mock('axios');
jest.mock('./data/hooks', () => ({
  useBadges: jest.fn(),
}));

jest.mock('./hooks/useBadges', () => ({
  useBadges: jest.fn(),
}));

describe('Badges Component', () => {
  afterEach(cleanup);

  beforeEach(() => {
    useBadges.mockReturnValue({
      isError: false,
      isLoading: false,
      badgesData: [],
      actionsData: [],
      coursesData: [],
      firstBadgeRef: null,
      submitStatus: submitBtnStatuses.DEFAULT,
      showErrorAlert: false,
      showErrorToast: false,
      deletionStatus: submitBtnStatuses.DEFAULT,
      setSubmitStatus: jest.fn(),
      setShowErrorToast: jest.fn(),
      setShowErrorAlert: jest.fn(),
      organizationsData: [],
      handleCreateNewBadge: jest.fn(),
      openManageEntityModal: jest.fn(),
      showBadgeCreatedAlert: false,
      handleDeleteBadgeById: jest.fn(),
      closeManageEntityModal: jest.fn(),
      isManageEntityModalOpen: false,
      openConfirmDeletionAlert: jest.fn(),
      closeDeletionManageEntityModal: jest.fn(),
      isDeletionManageEntityModalOpen: false,
    });
  });

  it('renders the footer on the page', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByRole } = renderWithProviders(<Badges />);

    const footer = getByRole('contentinfo');
    expect(footer).toBeInTheDocument();
  });

  it('displays the correct page heading', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });
    const { getByRole } = renderWithProviders(<Badges />);

    const heading = getByRole('heading', {
      level: 1, name: moduleMessages.pageTitle.defaultMessage,
    });
    expect(heading).toBeInTheDocument();
  });

  it('shows a loading spinner when the page is loading', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: true, isError: false });
    const { getByRole } = renderWithProviders(<Badges />);

    const spinner = getByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  it('displays an error message when the page fails to load badges', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: true });
    const { getByText, getByRole } = renderWithProviders(<Badges />);

    const errorHeading = getByText(genericMessages.alertDangerTitle.defaultMessage);
    expect(errorHeading).toBeInTheDocument();
    const errorMessage = getByText(genericMessages.alertDangerDescription.defaultMessage);
    expect(errorMessage).toBeInTheDocument();
    const dismissButton = getByRole('button', { name: 'Dismiss' });
    expect(dismissButton).toBeInTheDocument();
  });

  it('renders an empty badges list message when no badges are available', async () => {
    useBadges.mockReturnValue({ badgesData: [], isLoading: false, isError: false });
    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(moduleMessages.alertEmptyBadgesListTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(moduleMessages.alertEmptyBadgesListDescription.defaultMessage)).toBeInTheDocument();
  });

  it('shows the correct number of edit and delete buttons for each badge', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText, getAllByRole } = renderWithProviders(<Badges />);

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
    });

    const editButtons = getAllByRole('button', {
      name: moduleMessages.badgeEditBtnTitle.defaultMessage,
    });
    const deleteButtons = getAllByRole('button', {
      name: moduleMessages.badgeDeleteBtnTitle.defaultMessage,
    });

    expect(editButtons).toHaveLength(badgesMocks.length);
    expect(deleteButtons).toHaveLength(badgesMocks.length);
  });

  it('correctly displays the total number of badges on the page', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(
      moduleMessages.totalBadgesCount.defaultMessage.replace('{badgesCount}', badgesMocks.length),
    )).toBeInTheDocument();
  });
});

describe('fetchBadgesData API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches badge data successfully from API', async () => {
    axios.get.mockResolvedValueOnce({ data: badgesMocks.reverse() });

    const data = await fetchBadgesData();

    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
    expect(convertKeysToSnakeCase(data.reverse())).toEqual(badgesMocks);
  });

  it('throws an error when API request fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network Error'));

    await expect(fetchBadgesData()).rejects.toThrow('Network Error');
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
  });
});

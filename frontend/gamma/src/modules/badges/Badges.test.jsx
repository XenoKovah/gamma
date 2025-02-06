import React from 'react';
import '@testing-library/jest-dom';
import { waitFor, within, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';

import { useTranslate } from '../../i18n/utils';
import { renderWithProviders } from '../../setupTests';
import appMessages from '../../i18n/en';
import moduleMessages from './i18n/en';
import { useBadgesData, fetchBadgesData, API_ROUTES } from './data';
import { Badges } from '.';

import { badgesMocks } from './__mocks__';

jest.mock('axios');
jest.mock('./data/hooks', () => ({
  useBadgesData: jest.fn(),
}));

jest.mock('../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('Badges Component', () => {
  const translations = {
    'modules.badges.button.add-badge': moduleMessages['modules.badges.button.add-badge'].defaultMessage,
    'generic.alert.danger.title': appMessages['generic.alert.danger.title'].defaultMessage,
    'generic.alert.danger.description': appMessages['generic.alert.danger.description'].defaultMessage,
    'generic.alert.button.close.title': appMessages['generic.alert.button.close.title'].defaultMessage,
    'modules.badges.modal.add-badge.title': moduleMessages['modules.badges.modal.add-badge.title'].defaultMessage,
  };

  afterEach(cleanup);

  beforeEach(() => {
    jest.clearAllMocks();
    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  it('renders loader while loading', () => {
    useBadgesData.mockReturnValue({ data: [], isLoading: true, isError: false });

    const { getByRole } = renderWithProviders(<Badges />);
    expect(getByRole('status')).toBeInTheDocument();
  });

  it('renders error alert when API request fails', () => {
    useBadgesData.mockReturnValue({ data: [], isLoading: false, isError: true });

    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(translations['generic.alert.danger.title'])).toBeInTheDocument();
    expect(getByText(translations['generic.alert.danger.description'])).toBeInTheDocument();
  });

  it('closes error alert when close button is clicked', async () => {
    useBadgesData.mockReturnValue({ data: [], isLoading: false, isError: true });

    const { getByText, queryByText, getByRole } = renderWithProviders(<Badges />);
    expect(getByText(translations['generic.alert.danger.title'])).toBeInTheDocument();

    userEvent.click(getByRole('button', { name: translations['generic.alert.button.close.title'] }));

    await waitFor(() => {
      expect(queryByText(translations['generic.alert.danger.title'])).not.toBeInTheDocument();
    });
  });

  it('renders badges list and add badge button when API request succeeds', async () => {
    useBadgesData.mockReturnValue({ data: badgesMocks, isLoading: false, isError: false });

    const { getByText, getByTestId } = renderWithProviders(<Badges />);

    await waitFor(() => {
      expect(getByTestId('add-badge-button')).toBeInTheDocument();
    });

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
    });
  });

  it('displays error message correctly when API fails', async () => {
    useBadgesData.mockReturnValue({ data: [], isLoading: false, isError: true });

    const { getByRole } = renderWithProviders(<Badges />);

    await waitFor(() => {
      const errorAlert = getByRole('alert');
      expect(
        within(errorAlert).getByText(translations['generic.alert.danger.title']),
      ).toBeInTheDocument();
      expect(
        within(errorAlert).getByText(translations['generic.alert.danger.description']),
      ).toBeInTheDocument();
    });
  });

  it('opens the badge modal when the "Add Badge" button is clicked', async () => {
    useBadgesData.mockReturnValue({ data: badgesMocks, isLoading: false, isError: false });

    const { getByRole, getByTestId } = renderWithProviders(<Badges />);

    const addBadgeBtn = getByTestId('add-badge-button');

    userEvent.click(addBadgeBtn);
    waitFor(() => {
      const badgeModal = getByRole('dialog');
      expect(within(badgeModal).getByText(translations['modules.badges.modal.add-badge.title'])).toBeInTheDocument();
    });
  });
});

describe('fetchBadgesData API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches badge data successfully from API', async () => {
    axios.get.mockResolvedValueOnce({ data: badgesMocks });

    const data = await fetchBadgesData();

    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
    expect(data).toEqual(badgesMocks);
  });

  it('throws an error when API request fails', async () => {
    axios.get.mockRejectedValueOnce(new Error('Network Error'));

    await expect(fetchBadgesData()).rejects.toThrow('Network Error');
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith(API_ROUTES.BADGES);
  });
});

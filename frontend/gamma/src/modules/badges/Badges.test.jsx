import React from 'react';
import axios from 'axios';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { useTranslate } from '../../i18n/utils';
import { renderWithProviders } from '../../setupTests';
import appMessages from '../../i18n/en';
import { submitBtnStatuses } from '../../generic/status-button';
import { useBadges } from './hooks/useBadges';
import { convertKeysToSnakeCase } from './data/utils';
import moduleMessages from './i18n/en';
import { fetchBadgesData, API_ROUTES } from './data';
import { Badges } from '.';

import { badgesMocks } from './__mocks__';

jest.mock('axios');
jest.mock('./data/hooks', () => ({
  useBadges: jest.fn(),
}));

jest.mock('../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

jest.mock('./hooks/useBadges', () => ({
  useBadges: jest.fn(),
}));

describe('Badges Component', () => {
  const translations = {
    'generic.header.button.sing.out.text': appMessages['generic.header.button.sing.out.text'].defaultMessage,
    'modules.badges.button.add-badge': moduleMessages['modules.badges.button.add-badge'].defaultMessage,
    'generic.alert.danger.title': appMessages['generic.alert.danger.title'].defaultMessage,
    'generic.alert.danger.description': appMessages['generic.alert.danger.description'].defaultMessage,
    'generic.alert.button.close.title': appMessages['generic.alert.button.close.title'].defaultMessage,
    'modules.badges.modal.add-badge.title': moduleMessages['modules.badges.modal.add-badge.title'].defaultMessage,
    'modules.badges.heading.text': moduleMessages['modules.badges.heading.text'].defaultMessage,
    'modules.badges.alert.empty-badges-list.title': moduleMessages['modules.badges.alert.empty-badges-list.title'].defaultMessage,
    'generic.loader.screenReader.text': appMessages['generic.loader.screenReader.text'].defaultMessage,
    'modules.badges.alert.modal.confirm.deletion.title': moduleMessages['modules.badges.alert.modal.confirm.deletion.title'].defaultMessage,
    'modules.badges.alert.modal.confirm.deletion.description': moduleMessages['modules.badges.alert.modal.confirm.deletion.description'].defaultMessage,
    'generic.modal.alert.button.stateful.default.text': appMessages['generic.modal.alert.button.stateful.default.text'].defaultMessage,
    'generic.modal.alert.button.cancel.text': appMessages['generic.modal.alert.button.cancel.text'].defaultMessage,
    'modules.badges.alert.empty-badges-list.description': moduleMessages['modules.badges.alert.empty-badges-list.description'].defaultMessage,
    'modules.badges.total-badges.counter.text': moduleMessages['modules.badges.total-badges.counter.text'].defaultMessage,
    'modules.badges.badge-item.button.edit.title': moduleMessages['modules.badges.badge-item.button.edit.title'].defaultMessage,
    'modules.badges.badge-item.button.delete.title': moduleMessages['modules.badges.badge-item.button.delete.title'].defaultMessage,
    'generic.modal.dialog.button.stateful.default.text': appMessages['generic.modal.dialog.button.stateful.default.text'].defaultMessage,
    'generic.modal.dialog.button.cancel.text': appMessages['generic.modal.dialog.button.cancel.text'].defaultMessage,
    'generic.modal.entity.rules.button.add-new-rule.text': appMessages['generic.modal.entity.rules.button.add-new-rule.text'].defaultMessage,
    'generic.modal.entity.rules.alert.no-rules.description': appMessages['generic.modal.entity.rules.alert.no-rules.description'].defaultMessage,
    'generic.modal.entity.rules.alert.no-rules.heading': appMessages['generic.modal.entity.rules.alert.no-rules.heading'].defaultMessage,
    'generic.modal.entity.rules.heading': appMessages['generic.modal.entity.rules.heading'].defaultMessage,
    'generic.modal.entity.image.button.upload': appMessages['generic.modal.entity.image.button.upload'].defaultMessage,
    'generic.modal.entity.image.heading': appMessages['generic.modal.entity.image.heading'].defaultMessage,
    'generic.modal.entity.is-active.text': appMessages['generic.modal.entity.is-active.text'].defaultMessage,
    'generic.modal.entity.information.label.entity.description': appMessages['generic.modal.entity.information.label.entity.description'].defaultMessage,
    'generic.modal.entity.information.label.entity.slug': appMessages['generic.modal.entity.information.label.entity.slug'].defaultMessage,
    'generic.modal.entity.information.label.entity.title': appMessages['generic.modal.entity.information.label.entity.title'].defaultMessage,
    'generic.modal.entity.information.heading': appMessages['generic.modal.entity.information.heading'].defaultMessage,
  };

  afterEach(cleanup);

  beforeEach(() => {
    jest.clearAllMocks();
    useTranslate.mockImplementation((key, values) => (key === 'modules.badges.total-badges.counter.text'
      ? translations[key].replace('{badgesCount}', values?.badgesCount || 0)
      : translations[key] || key));
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
      level: 1, name: translations['modules.badges.heading.text'],
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

    const errorHeading = getByText(translations['generic.alert.danger.title']);
    expect(errorHeading).toBeInTheDocument();
    const errorMessage = getByText(translations['generic.alert.danger.description']);
    expect(errorMessage).toBeInTheDocument();
    const dismissButton = getByRole('button', { name: 'Dismiss' });
    expect(dismissButton).toBeInTheDocument();
  });

  it('renders an empty badges list message when no badges are available', async () => {
    useBadges.mockReturnValue({ badgesData: [], isLoading: false, isError: false });
    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(translations['modules.badges.alert.empty-badges-list.title'])).toBeInTheDocument();
    expect(getByText(translations['modules.badges.alert.empty-badges-list.description'])).toBeInTheDocument();
  });

  it('shows the correct number of edit and delete buttons for each badge', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText, getAllByRole } = renderWithProviders(<Badges />);

    badgesMocks.forEach((badge) => {
      expect(getByText(badge.title)).toBeInTheDocument();
      expect(getByText(badge.description)).toBeInTheDocument();
    });

    const editButtons = getAllByRole('button', {
      name: translations['modules.badges.badge-item.button.edit.title'],
    });
    const deleteButtons = getAllByRole('button', {
      name: translations['modules.badges.badge-item.button.delete.title'],
    });

    expect(editButtons).toHaveLength(badgesMocks.length);
    expect(deleteButtons).toHaveLength(badgesMocks.length);
  });

  it('correctly displays the total number of badges on the page', async () => {
    useBadges.mockReturnValue({ badgesData: badgesMocks, isLoading: false, isError: false });

    const { getByText } = renderWithProviders(<Badges />);

    expect(getByText(
      translations['modules.badges.total-badges.counter.text'].replace('{badgesCount}', badgesMocks.length),
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

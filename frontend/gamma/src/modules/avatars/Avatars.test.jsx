import React from 'react';
import '@testing-library/jest-dom';
import {
  cleanup, waitFor, within, act,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

import { submitBtnStatuses } from '../../generic/status-button';
import { renderWithProviders } from '../../setupTests';
import genericMessages from '../../i18n';
import { useAvatarSets } from './hooks/useAvatarSets';
import { fetchAvatarSetsData, API_ROUTES } from './data';
import { avatarSetsMocks } from './__mocks__';
import moduleMessages from './i18n';
import { Avatars } from '.';

jest.mock('./hooks/useAvatarSets', () => ({
  useAvatarSets: jest.fn(),
}));

describe('Avatars Component', () => {
  let mock;

  afterEach(() => {
    mock.restore();
    cleanup();
  });

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  beforeEach(() => {
    useAvatarSets.mockReturnValue({
      deletionStatus: submitBtnStatuses.DEFAULT,
      showErrorToast: false,
      showErrorAlert: false,
      avatarSetsData: [],
      setShowErrorToast: jest.fn(),
      setShowErrorAlert: jest.fn(),
      isAvatarSetsDataError: false,
      isAvatarSetsDataLoading: false,
      openConfirmDeletionModal: jest.fn(),
      handleDeleteAvatarSetById: jest.fn(),
      closeDeletionAvatarSetModal: jest.fn(),
      isDeletionAvatarSetModalOpen: false,
    });
  });

  it('check loading spinner', async () => {
    useAvatarSets.mockReturnValue({ isAvatarSetsDataLoading: true });
    const { getByRole } = renderWithProviders(<Avatars />);

    const loadingSpinner = getByRole('status');
    expect(loadingSpinner).toBeInTheDocument();
  });

  it('renders the footer on the page', async () => {
    const { getByRole } = renderWithProviders(<Avatars />);

    await waitFor(() => {
      const footer = getByRole('contentinfo');
      expect(footer).toBeInTheDocument();
    });
  });

  it('check error alert', async () => {
    useAvatarSets.mockReturnValue({ isAvatarSetsDataError: true });
    const { getByRole } = renderWithProviders(<Avatars />);

    const errorAlert = getByRole('alert');
    expect(within(errorAlert).getByText(genericMessages.alertDangerTitle.defaultMessage)).toBeInTheDocument();
    expect(within(errorAlert).getByText(genericMessages.alertDangerDescription.defaultMessage)).toBeInTheDocument();
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

    expect(getByText(
      moduleMessages.alertEmptyAvatarsListTitle.defaultMessage,
    )).toBeInTheDocument();
    expect(getByText(
      moduleMessages.alertEmptyAvatarsListDescription.defaultMessage,
    )).toBeInTheDocument();
  });

  it('correctly displays the total number of badges on the page', async () => {
    const { getByText } = renderWithProviders(<Avatars />);

    expect(getByText(
      moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', 0),
    )).toBeInTheDocument();
  });

  it('check render add avatar button', () => {
    const { getByTestId } = renderWithProviders(<Avatars />);

    const addAvatarBtn = getByTestId('add-avatar-button');
    expect(addAvatarBtn).toBeInTheDocument();
  });

  it('renders avatar items correctly with titles and buttons', async () => {
    useAvatarSets.mockReturnValue({ avatarSetsData: avatarSetsMocks });

    mock.onGet(API_ROUTES.AVATAR_SET).reply(200, avatarSetsMocks);

    await fetchAvatarSetsData();

    const { getByTestId, getByText } = renderWithProviders(<Avatars />);

    avatarSetsMocks.forEach((avatarSet) => {
      const avatarCard = getByTestId(`avatar-item-${avatarSet.id}`);
      expect(within(avatarCard).getByText(avatarSet.title)).toBeInTheDocument();
      expect(within(avatarCard).getByText(moduleMessages.avatarDeleteBtnTitle.defaultMessage)).toBeInTheDocument();
      expect(within(avatarCard).getByText(moduleMessages.avatarEditBtnTitle.defaultMessage)).toBeInTheDocument();
    });

    expect(getByText(
      moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', avatarSetsMocks.length),
    )).toBeInTheDocument();
  });

  it('handles delete avatar set correctly', async () => {
    const targetAvatarSetId = 12;
    let confirmDeletionModal;

    mock.onGet(API_ROUTES.AVATAR_SET).reply(200, avatarSetsMocks);
    await act(() => fetchAvatarSetsData());

    useAvatarSets.mockReturnValue({
      avatarSetsData: avatarSetsMocks,
      openConfirmDeletionModal: jest.fn(),
      isDeletionAvatarSetModalOpen: false,
    });

    const {
      rerender, getByTestId, getByText, getByRole,
    } = renderWithProviders(<Avatars />);

    const avatarCard = getByTestId(`avatar-item-${targetAvatarSetId}`);
    const deleteAvatarSetBtn = within(avatarCard).getByText(moduleMessages.avatarDeleteBtnTitle.defaultMessage);

    expect(getByText(
      moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', avatarSetsMocks.length),
    )).toBeInTheDocument();

    await act(async () => userEvent.click(deleteAvatarSetBtn));

    useAvatarSets.mockReturnValue({
      avatarSetsData: avatarSetsMocks,
      openConfirmDeletionModal: jest.fn(),
      isDeletionAvatarSetModalOpen: true,
    });

    rerender(<Avatars />);

    await waitFor(() => {
      confirmDeletionModal = getByRole('dialog');
      expect(within(confirmDeletionModal).getByText(
        moduleMessages.confirmDeletionModalTitle.defaultMessage,
      )).toBeInTheDocument();
      expect(within(confirmDeletionModal).getByText(
        moduleMessages.confirmDeletionModalDescription.defaultMessage,
      )).toBeInTheDocument();
    });

    const deleteBtn = within(confirmDeletionModal).getByText(moduleMessages.avatarDeleteBtnTitle.defaultMessage);

    const updatedAvatarSetsMocks = avatarSetsMocks.filter(avatarSet => avatarSet.id !== targetAvatarSetId);

    mock.onDelete(`${API_ROUTES.AVATAR_SET}${targetAvatarSetId}`).reply(200, updatedAvatarSetsMocks);

    await act(async () => userEvent.click(deleteBtn));

    await act(() => fetchAvatarSetsData());

    useAvatarSets.mockReturnValue({
      avatarSetsData: updatedAvatarSetsMocks,
      openConfirmDeletionModal: jest.fn(),
      isDeletionAvatarSetModalOpen: false,
    });

    rerender(<Avatars />);

    await waitFor(() => {
      expect(getByText(
        moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', updatedAvatarSetsMocks.length),
      )).toBeInTheDocument();
    });
  });
});

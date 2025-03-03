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
import {
  fetchAvatarSetsData, API_ROUTES, createAvatarSet, convertKeysToCamelCase,
} from './data';
import { avatarSetsMocks } from './__mocks__';
import moduleMessages from './i18n';
import { Avatars } from '.';

jest.mock('./hooks/useAvatarSets', () => ({
  useAvatarSets: jest.fn(),
}));

describe('Avatars', () => {
  let mock;

  const getMockedUseAvatarSets = (overrides = {}) => ({
    activeToast: null,
    submitStatus: submitBtnStatuses.DEFAULT,
    deletionStatus: submitBtnStatuses.DEFAULT,
    showErrorAlert: false,
    avatarSetsData: [],
    setShowErrorAlert: jest.fn(),
    isAvatarSetsDataError: false,
    isAvatarSetsDataLoading: false,
    openConfirmDeletionModal: jest.fn(),
    handleCreateNewAvatarSet: jest.fn(),
    openManageAvatarSetModal: jest.fn(),
    handleDeleteAvatarSetById: jest.fn(),
    closeManageAvatarSetModal: jest.fn(),
    isManageAvatarSetModalOpen: false,
    closeDeletionAvatarSetModal: jest.fn(),
    isDeletionAvatarSetModalOpen: false,
    showAvatarSetCreatedSuccessfully: false,
    ...overrides,
  });

  beforeEach(() => {
    mock = new MockAdapter(axios);
    useAvatarSets.mockReturnValue(getMockedUseAvatarSets());
  });

  afterEach(() => {
    mock.restore();
    cleanup();
    useAvatarSets.mockReset();
  });

  it('shows a loading spinner', async () => {
    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isAvatarSetsDataLoading: true }));

    const { getByRole } = renderWithProviders(<Avatars />);
    expect(getByRole('status')).toBeInTheDocument();
  });

  it('renders the footer on the page', async () => {
    const { getByRole } = renderWithProviders(<Avatars />);
    await waitFor(() => getByRole('contentinfo'));
  });

  it('shows an error alert when data fetching fails', async () => {
    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isAvatarSetsDataError: true }));

    const { getByRole } = renderWithProviders(<Avatars />);

    const errorAlert = getByRole('alert');
    within(errorAlert).getByText(genericMessages.alertDangerTitle.defaultMessage);
    within(errorAlert).getByText(genericMessages.alertDangerDescription.defaultMessage);
  });

  it('displays the correct page heading', async () => {
    const { getByRole } = renderWithProviders(<Avatars />);
    getByRole('heading', { level: 1, name: moduleMessages.pageTitle.defaultMessage });
  });

  it('renders an empty avatars list message', async () => {
    const { getByText } = renderWithProviders(<Avatars />);

    getByText(moduleMessages.alertEmptyAvatarSetListTitle.defaultMessage);
    getByText(moduleMessages.alertEmptyAvatarSetListDescription.defaultMessage);
  });

  it('displays the total number of avatar sets correctly', async () => {
    const { getByText } = renderWithProviders(<Avatars />);
    getByText(moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', 0));
  });

  it('renders add avatar set button', () => {
    const { getByTestId } = renderWithProviders(<Avatars />);
    expect(getByTestId('add-avatar-set-button')).toBeInTheDocument();
  });

  it('renders avatar set items correctly with titles and buttons', async () => {
    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({
      avatarSetsData: convertKeysToCamelCase(avatarSetsMocks),
    }));

    mock.onGet(API_ROUTES.AVATAR_SET).reply(200, convertKeysToCamelCase(avatarSetsMocks));
    await fetchAvatarSetsData();

    const { getByTestId, getByText } = renderWithProviders(<Avatars />);

    avatarSetsMocks.forEach((avatarSet) => {
      const avatarCard = getByTestId(`avatar-set-item-${avatarSet.id}`);
      within(avatarCard).getByText(avatarSet.title);
      within(avatarCard).getByText(moduleMessages.avatarSetDeleteBtnTitle.defaultMessage);
      within(avatarCard).getByText(moduleMessages.avatarSetEditBtnTitle.defaultMessage);
    });

    getByText(moduleMessages.totalAvatarSetsCount.defaultMessage.replace(
      '{avatarSetsCount}',
      avatarSetsMocks.length,
    ));
  });

  it('handles deleting an avatar set correctly', async () => {
    const targetAvatarSetId = 12;

    mock.onGet(API_ROUTES.AVATAR_SET).reply(200, convertKeysToCamelCase(avatarSetsMocks));
    await act(() => fetchAvatarSetsData());

    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({
      avatarSetsData: convertKeysToCamelCase(avatarSetsMocks),
    }));

    const {
      rerender, getByTestId, getByRole, getByText,
    } = renderWithProviders(<Avatars />);
    const avatarSetCard = getByTestId(`avatar-set-item-${targetAvatarSetId}`);
    const deleteAvatarSetBtn = within(avatarSetCard).getByText(moduleMessages.avatarSetDeleteBtnTitle.defaultMessage);

    await act(async () => userEvent.click(deleteAvatarSetBtn));

    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({
      isDeletionAvatarSetModalOpen: true,
    }));

    rerender(<Avatars />);

    await waitFor(() => {
      const confirmAvatarSetDeletionModal = getByRole('dialog');
      within(confirmAvatarSetDeletionModal).getByText(moduleMessages.confirmDeletionModalTitle.defaultMessage);
    });

    const avatarSetDeleteBtn = getByText(moduleMessages.avatarSetDeleteBtnTitle.defaultMessage);
    const updatedAvatarSetsMocks = convertKeysToCamelCase(avatarSetsMocks).filter(
      avatarSet => avatarSet.id !== targetAvatarSetId,
    );

    mock.onDelete(`${API_ROUTES.AVATAR_SET}${targetAvatarSetId}`).reply(200, updatedAvatarSetsMocks);
    await act(async () => userEvent.click(avatarSetDeleteBtn));
    await act(() => fetchAvatarSetsData());

    useAvatarSets.mockReturnValue(getMockedUseAvatarSets({
      activeToast: {
        variant: 'success',
        text: moduleMessages.toastAvatarSetDeletedSuccessfullyTitle.defaultMessage,
        onClose: jest.fn(),
      },
      avatarSetsData: updatedAvatarSetsMocks,
    }));

    rerender(<Avatars />);

    await waitFor(() => {
      getByText(moduleMessages.totalAvatarSetsCount.defaultMessage.replace(
        '{avatarSetsCount}',
        updatedAvatarSetsMocks.length,
      ));
      within(document.querySelector('.toast-success'))
        .getByText(moduleMessages.toastAvatarSetDeletedSuccessfullyTitle.defaultMessage);
    });
  });

  describe('Avatar set stepper', () => {
    it('opens the avatar set stepper and displays all expected elements', async () => {
      const { rerender, getByTestId, getByRole } = renderWithProviders(<Avatars />);

      await act(async () => {
        userEvent.click(getByTestId('add-avatar-set-button'));
      });

      useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isManageAvatarSetModalOpen: true }));

      rerender(<Avatars />);

      await waitFor(() => {
        const avatarSetStepper = getByRole('dialog');

        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperTitle.defaultMessage);
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperBtnStatefulDefaultText.defaultMessage);
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperCloseBtnTitle.defaultMessage);

        // Steps
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperEvolutionStepTitle.defaultMessage);
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperAvatarsStepTitle.defaultMessage);
        within(avatarSetStepper).getByRole('heading', {
          level: 2,
          name: moduleMessages.avatarSetStepperTitleStepTitle.defaultMessage,
        });
      });
    });

    it('validates that the title input is required', async () => {
      const { rerender, getByTestId, getByRole } = renderWithProviders(<Avatars />);

      await act(async () => {
        userEvent.click(getByTestId('add-avatar-set-button'));
      });

      useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isManageAvatarSetModalOpen: true }));
      rerender(<Avatars />);

      await waitFor(() => {
        const avatarSetStepper = getByRole('dialog');
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperTitleStepDescription.defaultMessage);

        const titleInput = within(avatarSetStepper).getByLabelText(
          moduleMessages.avatarSetStepperTitleStepInputTitleLabel.defaultMessage,
        );

        userEvent.click(titleInput);
        userEvent.tab();
      });

      await waitFor(() => {
        const avatarSetStepper = getByRole('dialog');
        within(avatarSetStepper).getByText(moduleMessages.avatarSetStepperValidationTitleRequired.defaultMessage);
      });
    });

    it('allows the user to create a new avatar set and displays a success message', async () => {
      const {
        rerender, getByTestId, getByRole, getByText,
      } = renderWithProviders(<Avatars />);

      await act(async () => {
        userEvent.click(getByTestId('add-avatar-set-button'));
      });

      useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isManageAvatarSetModalOpen: true }));
      rerender(<Avatars />);

      await waitFor(() => {
        const avatarSetStepper = getByRole('dialog');

        const titleInput = within(avatarSetStepper).getByLabelText(
          moduleMessages.avatarSetStepperTitleStepInputTitleLabel.defaultMessage,
        );

        userEvent.type(titleInput, 'Test avatar set 1');
        userEvent.tab();

        expect(
          within(avatarSetStepper).queryByText(moduleMessages.avatarSetStepperValidationTitleRequired.defaultMessage),
        ).not.toBeInTheDocument();

        const nextBtn = within(avatarSetStepper)
          .getByText(moduleMessages.avatarSetStepperBtnStatefulDefaultText.defaultMessage);
        userEvent.click(nextBtn);
      });

      const newAvatarSet = {
        id: avatarSetsMocks.length + 1,
        title: 'Test avatar set 1',
        avatars: [],
        use_in_courses: [],
        is_draft: true,
      };

      const updatedAvatarSetsMocks = [...avatarSetsMocks, newAvatarSet];

      mock.onPost(API_ROUTES.AVATAR_SET).reply(200, updatedAvatarSetsMocks);

      await waitFor(() => createAvatarSet(updatedAvatarSetsMocks));

      useAvatarSets.mockReturnValue(
        getMockedUseAvatarSets({
          activeToast: {
            variant: 'success',
            text: moduleMessages.toastNewAvatarSetCreatedSuccessfullyTitle.defaultMessage,
            onClose: jest.fn(),
          },
          avatarSetsData: convertKeysToCamelCase(updatedAvatarSetsMocks),
          isManageAvatarSetModalOpen: true,
        }),
      );

      rerender(<Avatars />);

      await waitFor(() => {
        const successToast = document.querySelector('.toast-success');

        within(successToast).getByText(moduleMessages.toastNewAvatarSetCreatedSuccessfullyTitle.defaultMessage);

        getByText(
          moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', updatedAvatarSetsMocks.length),
        );
      });
    });
  });
});

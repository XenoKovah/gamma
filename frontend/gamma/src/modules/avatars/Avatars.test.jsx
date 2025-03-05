import React from 'react';
import '@testing-library/jest-dom';
import {
  cleanup, waitFor, within, act,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

import { useAvatarsContext } from './context/AvatarsContext';

import { submitBtnStatuses } from '../../generic/status-button';
import { renderWithProviders } from '../../setupTests';
import genericMessages from '../../i18n';
import { useAvatarSets } from './hooks/useAvatarSets';
import {
  fetchAvatarSetsData, API_ROUTES, createAvatarSet,
  convertKeysToCamelCase, updateAvatarSet,
} from './data';
import { avatarSetsMocks } from './__mocks__';
import moduleMessages from './i18n';
import { Avatars } from '.';

jest.mock('./hooks/useAvatarSets', () => ({
  useAvatarSets: jest.fn(),
}));

jest.mock('./context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

const mockHandleCreateNewAvatarSet = jest.fn()
  .mockImplementation((_, callback) => Promise.resolve().then(() => callback()));

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
    handleCreateNewAvatarSet: mockHandleCreateNewAvatarSet,
    openManageAvatarSetModal: jest.fn(),
    handleDeleteAvatarSetById: jest.fn(),
    closeManageAvatarSetModal: jest.fn(),
    isManageAvatarSetModalOpen: false,
    closeDeletionAvatarSetModal: jest.fn(),
    isDeletionAvatarSetModalOpen: false,
    showAvatarSetCreatedSuccessfully: false,
    handleUpdateAvatarSet: jest.fn(),
    ...overrides,
  });

  beforeEach(() => {
    mock = new MockAdapter(axios);
    useAvatarSets.mockReturnValue(getMockedUseAvatarSets());

    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: null,
      setCurrentAvatarSetData: jest.fn(),
    });
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
    describe('Title step', () => {
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
              text: moduleMessages.toastNewAvatarSetSavedSuccessfullyTitle.defaultMessage,
              onClose: jest.fn(),
            },
            avatarSetsData: convertKeysToCamelCase(updatedAvatarSetsMocks),
            isManageAvatarSetModalOpen: true,
          }),
        );

        rerender(<Avatars />);

        await waitFor(() => {
          const successToast = document.querySelector('.toast-success');

          within(successToast).getByText(moduleMessages.toastNewAvatarSetSavedSuccessfullyTitle.defaultMessage);

          getByText(
            moduleMessages.totalAvatarSetsCount.defaultMessage.replace('{avatarSetsCount}', updatedAvatarSetsMocks.length),
          );
        });
      });
    });

    describe('Evolution step', () => {
      let rerender; let getByTestId; let getByRole;

      beforeEach(() => {
        ({
          rerender, getByTestId, getByRole,
        } = renderWithProviders(<Avatars />));
      });

      const openAvatarModal = async () => {
        await act(async () => {
          userEvent.click(getByTestId('add-avatar-set-button'));
        });

        useAvatarSets.mockReturnValue(getMockedUseAvatarSets({ isManageAvatarSetModalOpen: true }));
        rerender(<Avatars />);
      };

      const fillTitleAndGoNext = async (title = 'Test avatar set 1') => {
        await waitFor(async () => {
          const avatarSetStepper = getByRole('dialog');
          const titleInput = within(avatarSetStepper).getByRole('textbox', {
            name: moduleMessages.avatarSetStepperTitleStepInputTitleLabel.defaultMessage,
          });

          await userEvent.type(titleInput, title, { delay: 50 });

          const nextBtn = within(avatarSetStepper)
            .getByRole('button', { name: moduleMessages.avatarSetStepperBtnStatefulDefaultText.defaultMessage });

          userEvent.click(nextBtn);
        });
      };

      const mockAvatarSetCreation = async (title = 'Test avatar set 1') => {
        const newAvatarSet = {
          id: avatarSetsMocks.length + 1,
          title,
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
              text: moduleMessages.toastNewAvatarSetSavedSuccessfullyTitle.defaultMessage,
              onClose: jest.fn(),
            },
            avatarSetsData: convertKeysToCamelCase(updatedAvatarSetsMocks),
            isManageAvatarSetModalOpen: true,
          }),
        );

        rerender(<Avatars />);
      };

      const uploadFiles = async (files) => {
        const avatarSetStepper = await waitFor(() => getByRole('dialog'));

        await waitFor(() => {
          expect(within(avatarSetStepper).getAllByTestId('dropzone-container')).toHaveLength(files.length);
        });

        for (let i = 0; i < files.length; i += 1) {
          const dropzoneInput = within(avatarSetStepper)
            .getAllByTestId('dropzone-container')[i]
            .querySelector('input[type="file"]');

          expect(dropzoneInput).toBeInTheDocument();

          await act(async () => { // eslint-disable-line no-await-in-loop
            userEvent.upload(dropzoneInput, files[i]);
          });
        }
      };

      const assertImagesUploaded = async (count) => {
        await waitFor(() => {
          const uploadedImages = within(getByRole('dialog')).getAllByRole('img');
          expect(uploadedImages).toHaveLength(count);
        });
      };

      it('should render the evolution step correctly', async () => {
        await openAvatarModal();
        await fillTitleAndGoNext();
        await mockAvatarSetCreation();

        await waitFor(() => {
          const avatarSetStepper = getByRole('dialog');
          expect(within(avatarSetStepper).getByRole('heading', {
            level: 2,
            name: moduleMessages.avatarSetStepperEvolutionStepTitle.defaultMessage,
          })).toBeInTheDocument();

          expect(within(avatarSetStepper)
            .getByText(genericMessages.pgnDropzoneDefaultContentLabel.defaultMessage)).toBeInTheDocument();
          expect(within(avatarSetStepper).getByRole('button', {
            name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage,
          })).toBeInTheDocument();
        });
      });

      it('should add a new evolution stage correctly', async () => {
        await openAvatarModal();
        await fillTitleAndGoNext();
        await mockAvatarSetCreation();

        await waitFor(() => {
          const avatarSetStepper = getByRole('dialog');

          const addEvolutionStageBtn = within(avatarSetStepper)
            .getByRole('button', { name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage });

          expect(within(avatarSetStepper).getAllByTestId('dropzone-container')).toHaveLength(1);

          userEvent.click(addEvolutionStageBtn);
        });

        await waitFor(() => {
          expect(within(getByRole('dialog')).getAllByTestId('dropzone-container')).toHaveLength(2);
        });
      });

      it('should remove an evolution stage correctly', async () => {
        await openAvatarModal();
        await fillTitleAndGoNext();
        await mockAvatarSetCreation();

        await waitFor(() => {
          const avatarSetStepper = getByRole('dialog');
          const removeEvolutionStageBtn = within(avatarSetStepper)
            .getByRole('button', { name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage });

          expect(within(avatarSetStepper).getAllByTestId('dropzone-container')).toHaveLength(1);

          userEvent.click(removeEvolutionStageBtn);
        });

        await waitFor(() => {
          expect(within(getByRole('dialog')).queryAllByTestId('dropzone-container')).toHaveLength(0);
        });
      });

      it('should successfully create and send request', async () => {
        await openAvatarModal();
        await fillTitleAndGoNext();
        await mockAvatarSetCreation();
        const avatarSetId = 123;

        const files = [
          new File(['avatar 1'], 'avatar1.svg', { type: 'image/svg+xml' }),
        ];

        await uploadFiles(files);

        const updatedAvatarSet = {
          id: avatarSetsMocks.length + 1,
          title: 'Test avatar set 1',
          avatars: [{ title: 'Avatar', description: 'Some description', image: '' }],
          use_in_courses: [],
          is_draft: true,
        };

        const updatedAvatarSetsMocks2 = [...avatarSetsMocks, updatedAvatarSet];

        mock.onPatch(`${API_ROUTES.AVATAR_SET}${avatarSetId}/`).reply(200, updatedAvatarSetsMocks2);

        await waitFor(() => updateAvatarSet({ id: avatarSetId, avatars: updatedAvatarSetsMocks2 }));

        useAvatarSets.mockReturnValue(
          getMockedUseAvatarSets({
            activeToast: {
              variant: 'success',
              text: moduleMessages.toastNewAvatarSetSavedSuccessfullyTitle.defaultMessage,
              onClose: jest.fn(),
            },
            avatarSetsData: convertKeysToCamelCase(updatedAvatarSetsMocks2),
            isManageAvatarSetModalOpen: true,
          }),
        );

        await assertImagesUploaded(1);
      });
    });
  });
});

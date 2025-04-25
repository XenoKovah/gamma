import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { Formik } from 'formik';

import { renderWithProviders } from '../../../../../../setupTests';
import { useAvatarsContext } from '../../../../context/AvatarsContext';
import genericMessages from '../../../../../../i18n';
import moduleMessages from '../../../../i18n';
import { STEPPER_STEPS } from '../../constants';
import EvolutionStep from '../EvolutionStep';

jest.mock('../../../../context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

jest.mock('@openedx/paragon', () => ({
  ...jest.requireActual('@openedx/paragon'),
  Stepper: {
    Step: jest.fn(({ children }) => <div data-testid="stepper-step">{children}</div>),
  },
}));

describe('EvolutionStep', () => {
  const mockSetCurrentStep = jest.fn();
  const mockHandleUpdateAvatarSet = jest.fn();
  const mockSetCurrentAvatarSetData = jest.fn();
  const mockHandleCloseManageAvatarSetModal = jest.fn();

  const defaultProps = {
    currentStep: STEPPER_STEPS.evolution,
    submitStatus: '',
    setCurrentStep: mockSetCurrentStep,
    handleUpdateAvatarSet: mockHandleUpdateAvatarSet,
    statefulButtonLabels: {
      default: genericMessages.modalDialogBtnStatefulDefaultText.defaultMessage,
      pending: moduleMessages.avatarSetStepperBtnStatefulPendingText.defaultMessage,
      complete: moduleMessages.avatarSetStepperBtnStatefulCompleteText.defaultMessage,
      finish: moduleMessages.avatarSetStepperBtnFinishText.defaultMessage,
    },
    handleCloseManageAvatarSetModal: mockHandleCloseManageAvatarSetModal,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: { avatars: [] },
      setCurrentAvatarSetData: mockSetCurrentAvatarSetData,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <Formik initialValues={{ avatars: [] }} onSubmit={jest.fn()}>
      <EvolutionStep {...defaultProps} {...props} />
    </Formik>,
  );

  it('renders EvolutionStep component with form elements', () => {
    const { getByRole, getByText } = renderComponent();

    expect(
      getByRole('heading', { name: moduleMessages.avatarSetStepperEvolutionStepTitle.defaultMessage }),
    ).toBeInTheDocument();
    expect(
      getByRole('button', { name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage }),
    ).toBeInTheDocument();

    expect(getByText(/to save your uploads to the avatar set. If you leave the page without clicking/i)).toBeInTheDocument();
    expect(getByText(/your images won't be saved/i)).toBeInTheDocument();
    expect(getByText(/If you add a new stage but don't upload an image,/i)).toBeInTheDocument();
    expect(getByText(/will remain disabled. To proceed, either upload an image or click/i)).toBeInTheDocument();
    expect(getByText(/to delete the empty stage/i)).toBeInTheDocument();
  });

  it('allows adding a new avatar stage and uploading an image to Stage 1', async () => {
    const { getAllByTestId, getByRole } = renderComponent();

    await waitFor(() => {
      const addEvolutionStageBtn = getByRole('button', {
        name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage,
      });
      userEvent.click(addEvolutionStageBtn);
    });

    await waitFor(() => {
      expect(getAllByTestId('dropzone-container')).toHaveLength(1);
    });

    const file = new File(['dummy content'], 'avatar.svg', { type: 'image/svg+xml' });

    await waitFor(() => {
      const fileInput = getAllByTestId('dropzone-container')[0].querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
      userEvent.upload(fileInput, file);
    });

    await waitFor(() => {
      const fileInput = getAllByTestId('dropzone-container')[0].querySelector('input[type="file"]');
      expect(fileInput.files[0]).toBe(file);
      expect(fileInput.files).toHaveLength(1);
    });

    await waitFor(() => {
      const addEvolutionStageBtn = getByRole('button', {
        name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage,
      });
      userEvent.click(addEvolutionStageBtn);
    });

    await waitFor(() => {
      expect(getAllByTestId('dropzone-container')).toHaveLength(1);
      const uploadedAvatarImg = getByRole('img');
      expect(uploadedAvatarImg).toBeInTheDocument();
      expect(uploadedAvatarImg).toHaveAttribute('src', 'data:image/svg+xml;base64,ZHVtbXkgY29udGVudA==');
    });
  });

  it('disables submit button if less than minimum avatars', async () => {
    const { getByRole } = renderComponent();

    const submitButton = getByRole('button', { name: defaultProps.statefulButtonLabels.default });
    expect(submitButton).toBeDisabled();
  });

  it('calls handleCloseManageAvatarSetModal when close button is clicked', async () => {
    const { getByRole } = renderComponent();

    const closeButton = getByRole('button', { name: moduleMessages.avatarSetStepperCloseBtnTitle.defaultMessage });
    userEvent.click(closeButton);

    expect(mockHandleCloseManageAvatarSetModal).toHaveBeenCalledTimes(1);
  });

  it('allows removing an avatar stage', async () => {
    const { getByRole, queryByTestId, getAllByTestId } = renderComponent();

    await waitFor(() => {
      const addEvolutionStageBtn = getByRole('button', {
        name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage,
      });
      userEvent.click(addEvolutionStageBtn);
    });

    await waitFor(() => {
      expect(getAllByTestId('dropzone-container')).toHaveLength(1);
    });

    await waitFor(() => {
      const removeButton = getByRole('button', {
        name: moduleMessages.avatarSetStepperEvolutionDeleteAvatarBtn.defaultMessage,
      });
      userEvent.click(removeButton);
    });

    await waitFor(() => {
      const deleteButton = getByRole('button', { name: genericMessages.alertBtnDeleteText.defaultMessage });
      userEvent.click(deleteButton);
    });

    await waitFor(() => {
      expect(queryByTestId('dropzone-container')).not.toBeInTheDocument();
    });
  });
});

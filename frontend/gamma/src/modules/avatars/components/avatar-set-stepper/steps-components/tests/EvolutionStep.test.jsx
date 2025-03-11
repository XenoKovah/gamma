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
    const { getByRole } = renderComponent();

    expect(
      getByRole('heading', { name: moduleMessages.avatarSetStepperEvolutionStepTitle.defaultMessage }),
    ).toBeInTheDocument();
    expect(
      getByRole('button', { name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage }),
    ).toBeInTheDocument();
  });

  // TOTO: Fix this test
  it.skip('allows adding a new avatar stage', async () => {
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

    await waitFor(() => {
      const addEvolutionStageBtn = getByRole('button', {
        name: moduleMessages.avatarSetStepperEvolutionAddStageBtn.defaultMessage,
      });
      userEvent.click(addEvolutionStageBtn);
    });

    await waitFor(() => {
      expect(getAllByTestId('dropzone-container')).toHaveLength(2);
    });
  });

  it('disables submit button if less than minimum avatars', async () => {
    const { getByRole } = renderComponent();

    const submitButton = getByRole('button', { name: defaultProps.statefulButtonLabels.default });
    expect(submitButton).toBeDisabled();
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
        name: moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn.defaultMessage,
      });
      userEvent.click(removeButton);
    });

    await waitFor(() => {
      expect(queryByTestId('dropzone-container')).not.toBeInTheDocument();
    });
  });
});

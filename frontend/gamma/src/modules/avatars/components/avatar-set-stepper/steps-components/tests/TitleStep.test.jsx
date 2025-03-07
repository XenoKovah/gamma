import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import * as Yup from 'yup';

import { renderWithProviders } from '../../../../../../setupTests';
import { useAvatarsContext } from '../../../../context/AvatarsContext';
import genericMessages from '../../../../../../i18n';
import moduleMessages from '../../../../i18n';
import { STEPPER_STEPS } from '../../constants';
import TitleStep from '../TitleStep';

jest.mock('../../../../context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

jest.mock('@openedx/paragon', () => ({
  ...jest.requireActual('@openedx/paragon'),
  Stepper: {
    Step: jest.fn(({ children }) => <div data-testid="stepper-step">{children}</div>),
  },
}));

describe('TitleStep', () => {
  const mockSetCurrentStep = jest.fn();
  const mockHandleCloseManageAvatarSetModal = jest.fn();
  const mockHandleCreateNewAvatarSet = jest.fn();
  const mockHandleUpdateAvatarSet = jest.fn();
  const mockSetCurrentAvatarSetData = jest.fn();

  const validationSchema = Yup.object({
    title: Yup.string().required(
      genericMessages.modalEntityValidationTitleRequiredText.defaultMessage,
    ).max(50, moduleMessages.avatarSetStepperValidationTitleMaxLength.defaultMessage),
  });

  const defaultProps = {
    currentStep: STEPPER_STEPS.title,
    submitStatus: '',
    setCurrentStep: mockSetCurrentStep,
    statefulButtonLabels: {
      default: genericMessages.modalDialogBtnStatefulDefaultText.defaultMessage,
      pending: genericMessages.modalDialogBtnStatefulPendingText.defaultMessage,
      complete: genericMessages.modalDialogBtnStatefulCompleteText.defaultMessage,
      finish: moduleMessages.avatarSetStepperBtnFinishText.defaultMessage,
    },
    handleCloseManageAvatarSetModal: mockHandleCloseManageAvatarSetModal,
    handleCreateNewAvatarSet: mockHandleCreateNewAvatarSet,
    handleUpdateAvatarSet: mockHandleUpdateAvatarSet,
    validationSchema,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: null,
      setCurrentAvatarSetData: mockSetCurrentAvatarSetData,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <TitleStep {...defaultProps} {...props} />,
  );

  it('renders TitleStep component with form elements', () => {
    const { getByRole } = renderComponent();

    expect(
      getByRole('heading', {
        name: moduleMessages.avatarSetStepperTitleStepTitle.defaultMessage,
      }),
    ).toBeInTheDocument();
    expect(
      getByRole('textbox', {
        name: moduleMessages.avatarSetStepperTitleStepInputTitleLabel.defaultMessage,
      }),
    ).toBeInTheDocument();
    expect(
      getByRole('button', {
        name: defaultProps.statefulButtonLabels.default,
      }),
    ).toBeInTheDocument();
  });

  it('validates required title field', async () => {
    const { getByRole, getByText } = renderComponent();

    const input = getByRole('textbox');
    userEvent.click(input);
    userEvent.tab();

    await waitFor(() => {
      expect(getByText(
        genericMessages.modalEntityValidationTitleRequiredText.defaultMessage,
      )).toBeInTheDocument();
    });
  });

  it('does not allow titles longer than 50 characters', async () => {
    const { getByRole, getByText } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, 'A'.repeat(51));
    userEvent.tab();

    await waitFor(() => {
      expect(getByText(
        moduleMessages.avatarSetStepperValidationTitleMaxLength.defaultMessage,
      )).toBeInTheDocument();
    });
  });

  it('calls handleUpdateAvatarSet when updating an existing avatar set', async () => {
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: { title: 'Old Title' },
      setCurrentAvatarSetData: mockSetCurrentAvatarSetData,
    });

    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.clear(input);
    userEvent.type(input, 'New Title');

    const saveButton = getByRole('button', {
      name: defaultProps.statefulButtonLabels.default,
    });
    userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockHandleUpdateAvatarSet).toHaveBeenCalled();
    });
  });

  it('calls handleCreateNewAvatarSet when creating a new avatar set', async () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, 'New Avatar Set');

    const saveButton = getByRole('button', { name: defaultProps.statefulButtonLabels.default });
    userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockHandleCreateNewAvatarSet).toHaveBeenCalled();
    });
  });

  it('trims input value when field loses focus', async () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, '  Trimmed Title  ');
    userEvent.tab();

    await waitFor(() => {
      expect(input).toHaveValue('Trimmed Title');
    });
  });

  it('proceeds to the next step when the title is unchanged', async () => {
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: { title: 'Same Title' },
      setCurrentAvatarSetData: mockSetCurrentAvatarSetData,
    });

    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.clear(input);
    userEvent.type(input, 'Same Title');

    const saveButton = getByRole('button', {
      name: defaultProps.statefulButtonLabels.default,
    });
    userEvent.click(saveButton);

    await waitFor(() => {
      expect(mockSetCurrentStep).toHaveBeenCalledWith(STEPPER_STEPS.evolution);
    });
  });

  it('calls handleCloseManageAvatarSetModal when clicking the close button', () => {
    const { getByRole } = renderComponent();

    const closeButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperCloseBtnTitle.defaultMessage,
    });
    userEvent.click(closeButton);

    expect(mockHandleCloseManageAvatarSetModal).toHaveBeenCalled();
  });
});

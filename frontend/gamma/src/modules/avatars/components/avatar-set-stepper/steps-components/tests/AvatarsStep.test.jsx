import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import { useAvatarsContext } from '../../../../context/AvatarsContext';
import { renderWithProviders } from '../../../../../../setupTests';
import moduleMessages from '../../../../i18n';
import { STEPPER_STEPS } from '../../constants';
import AvatarsStep from '../AvatarsStep';

jest.mock('../../../../context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

jest.mock('@openedx/paragon', () => ({
  ...jest.requireActual('@openedx/paragon'),
  Stepper: {
    Step: jest.fn(({ children }) => <div data-testid="stepper-step">{children}</div>),
  },
}));

describe('AvatarsStep', () => {
  const mockSetCurrentStep = jest.fn();
  const mockHandleDeleteAvatar = jest.fn();
  const mockHandleUpdateAvatar = jest.fn();
  const mockHandleCloseManageAvatarSetModal = jest.fn();
  const mockSetSubmitStatus = jest.fn();

  const avatarSetsData = [
    {
      id: 1,
      title: 'Avatar Set 1',
      avatars: [
        { id: 101, title: 'Avatar 1', image: 'avatar1.png' },
        { id: 102, title: 'Avatar 2', image: 'avatar2.png' },
      ],
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: { id: 1 },
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <AvatarsStep
      currentStep={STEPPER_STEPS.avatars}
      setCurrentStep={mockSetCurrentStep}
      submitStatus="idle"
      deletionStatus="idle"
      setSubmitStatus={mockSetSubmitStatus}
      handleDeleteAvatar={mockHandleDeleteAvatar}
      handleUpdateAvatar={mockHandleUpdateAvatar}
      handleCloseManageAvatarSetModal={mockHandleCloseManageAvatarSetModal}
      avatarSetsData={avatarSetsData}
      actionsData={[]}
      coursesData={{ courses: [] }}
      organizationsData={{ organisations: [] }}
      {...props}
    />,
  );

  it('renders AvatarsStep with title and avatar cards', () => {
    const { getByText, getAllByRole } = renderComponent();

    expect(getByText('Avatar 1')).toBeInTheDocument();
    expect(getByText('Avatar 2')).toBeInTheDocument();
    expect(getAllByRole('button', {
      name: moduleMessages.avatarSetDeleteBtnTitle.defaultMessage,
    })).toHaveLength(2);
    expect(getAllByRole('button', {
      name: moduleMessages.avatarSetEditBtnTitle.defaultMessage,
    })).toHaveLength(2);
  });

  it('opens the deletion confirmation modal when Delete is clicked', async () => {
    const { getAllByRole, getByRole } = renderComponent();

    const deleteButton = getAllByRole('button', {
      name: moduleMessages.avatarSetDeleteBtnTitle.defaultMessage,
    })[0];
    userEvent.click(deleteButton);

    await waitFor(() => {
      expect(getByRole('heading', {
        name: moduleMessages.confirmDeletionModalTitle.defaultMessage,
      })).toBeInTheDocument();
    });
  });

  it('calls handleDeleteAvatar with correct id when delete is confirmed', async () => {
    const { getAllByRole, getByRole } = renderComponent();

    userEvent.click(getAllByRole('button', {
      name: moduleMessages.avatarSetDeleteBtnTitle.defaultMessage,
    })[0]);

    await waitFor(() => {
      expect(
        getByRole('button', { name: moduleMessages.avatarSetDeleteBtnTitle.defaultMessage }),
      ).toBeInTheDocument();
    });

    userEvent.click(getByRole('button', {
      name: moduleMessages.avatarSetDeleteBtnTitle.defaultMessage,
    }));

    await waitFor(() => {
      expect(mockHandleDeleteAvatar).toHaveBeenCalledWith(101, expect.any(Function));
    });
  });

  it('navigates to the previous step when clicking the back button', () => {
    const { getByRole } = renderComponent();

    userEvent.click(getByRole('button', {
      name: moduleMessages.avatarSetStepperPreviousBtnTitle.defaultMessage,
    }));

    expect(mockSetCurrentStep).toHaveBeenCalledWith(STEPPER_STEPS.evolution);
  });

  it('navigates to the next step when clicking the next button', async () => {
    const { getByRole } = renderComponent();

    const nextButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperPreviousBtnTitle.defaultMessage,
    });
    userEvent.click(nextButton);

    await waitFor(() => {
      expect(mockSetCurrentStep).toHaveBeenCalledWith(STEPPER_STEPS.evolution);
    });
  });
});

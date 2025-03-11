import React from 'react';
import { cleanup, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import { useAvatarsContext } from '../../../../context/AvatarsContext';
import { renderWithProviders } from '../../../../../../setupTests';
import { avatarSetsMocks } from '../../../../__mocks__';
import moduleMessages from '../../../../i18n';
import { STEPPER_STEPS } from '../../constants';
import FinishStep from '../FinishStep';

jest.mock('../../../../context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

jest.mock('@openedx/paragon', () => ({
  ...jest.requireActual('@openedx/paragon'),
  Stepper: {
    Step: jest.fn(({ children }) => <div data-testid="stepper-step">{children}</div>),
  },
}));

describe('FinishStep', () => {
  const mockSetCurrentStep = jest.fn();
  const mockHandleCloseManageAvatarSetModal = jest.fn();
  const mockHandleFinishAvatarSet = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useAvatarsContext.mockReturnValue({
      currentAvatarSetData: { id: 20 },
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <FinishStep
      currentStep={STEPPER_STEPS.finish}
      setCurrentStep={mockSetCurrentStep}
      avatarSetsData={avatarSetsMocks}
      handleFinishAvatarSet={mockHandleFinishAvatarSet}
      handleCloseManageAvatarSetModal={mockHandleCloseManageAvatarSetModal}
      {...props}
    />,
  );

  it('renders AvatarsFinish with title and avatar cards', () => {
    const { getByText, getAllByText } = renderComponent();

    expect(getByText('Avatar 1')).toBeInTheDocument();
    expect(getByText('Avatar 2')).toBeInTheDocument();
    expect(getByText('Avatar Description 1')).toBeInTheDocument();
    expect(getByText('Avatar Description 2')).toBeInTheDocument();
    expect(getAllByText(
      moduleMessages.avatarCardRuleSectionTitle.defaultMessage.replace('{count}', 1),
    )).toHaveLength(1);
  });

  it('displays rule details on click by rule collapse row', async () => {
    const { getByTestId } = renderComponent();
    const avatarCardWithRules = getByTestId('card-item-2');
    const checkRules = (rules) => {
      Object.entries({ ...rules.action, ...rules.filters }).forEach(([key, value]) => {
        const filterKeyElement = within(avatarCardWithRules).getByText(
          new RegExp(`${key === 'eventType' ? 'event type' : key}:`, 'i'),
        );
        expect(filterKeyElement).toBeInTheDocument();

        const val = typeof value === 'number' ? value.toString() : value;
        expect(within(filterKeyElement.closest('li')).getByText(val)).toBeInTheDocument();
      });
    };

    const ruleOneCollapseBtn = within(avatarCardWithRules).getByText(
      moduleMessages.avatarCardRuleSectionTitle.defaultMessage.replace('{count}', 1),
    );
    const ruleTwoCollapseBtn = within(avatarCardWithRules).getByText(
      moduleMessages.avatarCardRuleSectionTitle.defaultMessage.replace('{count}', 2),
    );

    expect(ruleOneCollapseBtn).toBeInTheDocument();
    expect(ruleTwoCollapseBtn).toBeInTheDocument();

    userEvent.click(ruleOneCollapseBtn);
    await waitFor(() => {
      checkRules(avatarSetsMocks[8].avatars[1].rules[0]);
    });

    userEvent.click(ruleOneCollapseBtn);
    userEvent.click(ruleTwoCollapseBtn);
    await waitFor(() => {
      checkRules(avatarSetsMocks[8].avatars[1].rules[1]);
    });
  });

  it('navigates to the previous step when clicking the back button', () => {
    const { getByRole } = renderComponent();

    userEvent.click(getByRole('button', {
      name: moduleMessages.avatarSetStepperPreviousBtnTitle.defaultMessage,
    }));

    expect(mockSetCurrentStep).toHaveBeenCalledWith(STEPPER_STEPS.avatars);
  });

  it('closes the modal when clicking the finish button', () => {
    const { getByRole } = renderComponent();

    userEvent.click(getByRole('button', {
      name: moduleMessages.avatarSetStepperBtnFinishText.defaultMessage,
    }));

    expect(mockHandleFinishAvatarSet).toHaveBeenCalled();
  });
});

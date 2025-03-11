import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../../setupTests';
import { StatusButton } from '../../../../../../generic';
import genericMessages from '../../../../../../i18n';
import moduleMessages from '../../../../i18n';
import StepFooter from '../StepFooter';

jest.mock('../../../../../../generic', () => ({
  StatusButton: jest.fn(() => <button data-testid="status-button" type="button">Stateful Button</button>),
}));

const statefulButtonLabels = {
  default: genericMessages.modalDialogBtnStatefulDefaultText.defaultMessage,
  pending: moduleMessages.avatarSetStepperBtnStatefulPendingText.defaultMessage,
  complete: moduleMessages.avatarSetStepperBtnStatefulCompleteText.defaultMessage,
  finish: moduleMessages.avatarSetStepperBtnFinishText.defaultMessage,
};

describe('StepFooter', () => {
  const mockPrevBtnOnClick = jest.fn();
  const mockNextBtnOnClick = jest.fn();
  const mockSubmitFn = jest.fn();

  const defaultProps = {
    prevBtnText: moduleMessages.avatarSetStepperPreviousBtnTitle.defaultMessage,
    prevBtnOnClick: mockPrevBtnOnClick,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<StepFooter {...defaultProps} {...props} />);

  it('renders the previous button and calls the callback when clicked', () => {
    const { getByRole } = renderComponent();

    const prevButton = getByRole('button', { name: defaultProps.prevBtnText });
    expect(prevButton).toBeInTheDocument();

    userEvent.click(prevButton);
    expect(mockPrevBtnOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders the next button and calls the callback when clicked', () => {
    const { getByRole } = renderComponent({
      nextBtnText: moduleMessages.avatarSetStepperBtnStatefulDefaultText.defaultMessage,
      nextBtnOnClick: mockNextBtnOnClick,
    });

    const nextButton = getByRole('button', {
      name: moduleMessages.avatarSetStepperBtnStatefulDefaultText.defaultMessage,
    });
    expect(nextButton).toBeInTheDocument();

    userEvent.click(nextButton);
    expect(mockNextBtnOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders a stateful button instead of the next button when isStatefulBtn is true', () => {
    const { getByTestId } = renderComponent({
      isStatefulBtn: true,
      submitFn: mockSubmitFn,
      statefulButtonLabels,
      submitStatus: 'default',
    });

    expect(getByTestId('status-button')).toBeInTheDocument();
    expect(StatusButton).toHaveBeenCalledWith(
      expect.objectContaining({
        options: expect.objectContaining({ submitFn: mockSubmitFn }),
      }),
      {},
    );
  });

  it('disables the stateful button when disabled prop is true', () => {
    renderComponent({
      isStatefulBtn: true,
      disabledNextBtn: true,
      statefulButtonLabels,
      submitStatus: 'default',
    });

    expect(StatusButton).toHaveBeenCalledWith(
      expect.objectContaining({
        options: expect.objectContaining({ disabled: true }),
      }),
      {},
    );
  });
});

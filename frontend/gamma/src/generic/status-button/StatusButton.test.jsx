import React from 'react';
import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../setupTests';
import StatusButton from './StatusButton';
import { submitBtnStatuses } from './constants';

describe('StatusButton', () => {
  const mockSubmitFn = jest.fn();
  const labels = { default: 'Submit', pending: 'Submitting...', complete: 'Done' };

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders the button with correct label', () => {
    const { getByRole } = renderWithProviders(
      <StatusButton variant="primary" options={{}} labels={labels} />,
    );

    waitFor(() => {
      const button = getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent(labels.default);
    });
  });

  it('calls submit function on click', () => {
    const { getByRole } = renderWithProviders(
      <StatusButton variant="primary" options={{ submitFn: mockSubmitFn }} labels={labels} />,
    );

    waitFor(() => {
      const button = getByRole('button');

      userEvent.click(button);

      expect(mockSubmitFn).toHaveBeenCalledTimes(1);
    });
  });

  it('is disabled when options.disabled is true', () => {
    const { getByRole } = renderWithProviders(
      <StatusButton variant="primary" options={{ disabled: true }} labels={labels} />,
    );

    waitFor(() => {
      const button = getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  it('passes correct variant and state to StatefulButton', () => {
    const { getByRole } = renderWithProviders(
      <StatusButton
        variant="secondary"
        options={{ submitStatus: submitBtnStatuses.PENDING }}
        labels={labels}
      />,
    );

    waitFor(() => {
      const button = getByRole('button');
      expect(button).toHaveClass('secondary');
      expect(button).toHaveAttribute('data-state', submitBtnStatuses.PENDING);
    });
  });
});

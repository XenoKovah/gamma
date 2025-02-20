import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../../setupTests';
import DatePickerFormControl from '../DatePickerFormControl';

describe('DatePickerFormControl Component', () => {
  const mockOnClick = jest.fn();
  const mockOnBlur = jest.fn();

  const defaultProps = {
    value: '2024-01-01',
    onClick: mockOnClick,
    onBlur: mockOnBlur,
    className: 'test-class',
    placeholder: 'Select a date',
  };

  const renderComponent = (props = {}) => renderWithProviders(<DatePickerFormControl {...defaultProps} {...props} />);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  it('renders input with correct attributes', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue(defaultProps.value);
    expect(input).toHaveClass('has-value form-control');
  });

  it('calls onClick when input is clicked', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.click(input);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick for other keys', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.tab(input);

    expect(mockOnClick).not.toHaveBeenCalled();
  });

  it('input is focusable via tab', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    expect(input).toHaveAttribute('tabIndex', '0');
  });
});

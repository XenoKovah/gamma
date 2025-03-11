import React from 'react';
import { cleanup, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../../setupTests';
import { DATE_TYPES } from '../../../../constants';
import IntervalDatePicker from '..';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

const shortDays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
const fullDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

describe('IntervalDatePicker', () => {
  const mockSetFieldValue = jest.fn();
  const mockSetTouched = jest.fn();
  const pickerDateRef = { current: { setOpen: jest.fn() } };

  const defaultProps = {
    pickerDateRef,
    rule: {
      filters: {
        interval: {
          start: '2024-01-01',
          end: '2024-01-10',
        },
      },
    },
    ruleIndex: 0,
    dateType: DATE_TYPES.START,
    placeholder: 'Select a date',
    isDateTouched: false,
    validationErrorText: '',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      setFieldValue: mockSetFieldValue,
      setTouched: mockSetTouched,
      touched: { rules: [{ filters: { interval: {} } }] },
      errors: { rules: [{ filters: { interval: {} } }] },
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<IntervalDatePicker {...defaultProps} {...props} />);

  const verifyCalendarStructure = () => {
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/Next Month/i)).toBeInTheDocument();
    expect(screen.getByText(/January 2024/i)).toBeInTheDocument();

    shortDays.forEach((day) => {
      expect(screen.getByText(day)).toBeInTheDocument();
    });

    fullDays.forEach((day) => {
      expect(screen.getByLabelText(day)).toBeInTheDocument();
    });
  };

  const selectDate = (label, fieldPath, expectedValue) => {
    const targetDay = screen.getByLabelText(label);
    userEvent.click(targetDay);
    expect(mockSetFieldValue).toHaveBeenCalledWith(fieldPath, expectedValue);
  };

  it('renders date picker with correct placeholder, close button and input', () => {
    const { getByRole, getByText } = renderComponent();

    const input = getByRole('textbox');
    expect(input).toHaveValue(defaultProps.rule.filters.interval.start);

    expect(getByText(defaultProps.placeholder)).toBeInTheDocument();
    expect(getByRole('button', { name: 'Close' })).toBeInTheDocument();
  });

  // TODO: Fix this test
  it.skip('calls setFieldValue when a date is selected', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, '{enter}');

    verifyCalendarStructure();
    selectDate('Choose Saturday, 6 January 2024', 'rules.0.filters.interval.start', '2024-01-06T02:00:00');
  });

  it('displays validation error message when present', () => {
    const { getByText } = renderComponent({
      isDateTouched: true,
      validationErrorText: 'Invalid date',
    });

    expect(getByText('Invalid date')).toBeInTheDocument();
  });

  it('sets minDate for end date picker correctly', () => {
    const { getByRole } = renderComponent({ dateType: DATE_TYPES.END });

    const input = getByRole('textbox');
    expect(input).toHaveValue(defaultProps.rule.filters.interval.end);
    expect(getByRole('button', { name: 'Close' })).toBeInTheDocument();

    userEvent.type(input, '{enter}');

    verifyCalendarStructure();
    waitFor(() => {
      selectDate('Choose Wednesday, 10 January 2024', 'rules.0.filters.interval.end', '2024-01-10T00:00:00');
    });
  });

  it('does not set minDate when dateType is START', () => {
    renderComponent({ dateType: DATE_TYPES.START });
    const input = screen.getByRole('textbox');
    expect(input).toHaveValue(defaultProps.rule.filters.interval.start);
    userEvent.type(input, '{enter}');
    verifyCalendarStructure();
    expect(input).not.toHaveAttribute('minDate');
  });

  it('clears the date when clicking the clear button', async () => {
    renderComponent();
    const clearButton = screen.getByRole('button', { name: 'Close' });
    userEvent.click(clearButton);
    await waitFor(() => {
      expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.interval.start', null);
    });
  });
});

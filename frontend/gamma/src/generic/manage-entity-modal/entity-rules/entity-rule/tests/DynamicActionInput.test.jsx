import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import DynamicActionInput from '../DynamicActionInput';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('DynamicActionInput Component', () => {
  const mockSetFieldValue = jest.fn();
  const mockHandleBlur = jest.fn();
  const mockValues = {
    rules: [
      {
        action: {
          eventType: 'testAction',
          testField: '',
        },
      },
    ],
  };
  const mockTouched = {};
  const mockErrors = {};

  const mockData = {
    actions: [
      {
        eventName: 'testAction',
        schema: [
          {
            field: 'testField',
            title: 'Test Field',
          },
        ],
      },
    ],
  };

  const defaultProps = {
    ruleIndex: 0,
    data: mockData,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      values: mockValues,
      touched: mockTouched,
      errors: mockErrors,
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(
    <DynamicActionInput {...defaultProps} {...props} />,
  );

  it('renders nothing when no action type is selected', () => {
    useFormikContext.mockReturnValue({
      values: {
        rules: [
          {
            action: {},
          },
        ],
      },
      touched: mockTouched,
      errors: mockErrors,
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });

    const { queryByLabelText } = renderComponent();
    expect(queryByLabelText('Test Field')).not.toBeInTheDocument();
  });

  it('renders nothing when selected action has no schema', () => {
    useFormikContext.mockReturnValue({
      values: {
        rules: [
          {
            action: {
              eventType: 'nonExistentAction',
            },
          },
        ],
      },
      touched: mockTouched,
      errors: mockErrors,
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });

    const { queryByLabelText } = renderComponent();
    expect(queryByLabelText('Test Field')).not.toBeInTheDocument();
  });

  it('renders input field when action type and schema are present', () => {
    const { getByLabelText } = renderComponent();

    const input = getByLabelText('Test Field');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
  });

  it('displays error message when field is touched and has error', () => {
    useFormikContext.mockReturnValue({
      values: mockValues,
      touched: {
        rules: [
          {
            action: {
              testField: true,
            },
          },
        ],
      },
      errors: {
        rules: [
          {
            action: 'This is an error',
          },
        ],
      },
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });

    const { getByText } = renderComponent();
    expect(getByText('This is an error')).toBeInTheDocument();
  });

  it('updates form value when input changes', () => {
    const { getByLabelText } = renderComponent();

    const input = getByLabelText('Test Field');
    userEvent.type(input, '42');

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.testField', '42');
  });

  it('calls handleBlur when input loses focus', () => {
    const { getByLabelText } = renderComponent();

    const input = getByLabelText('Test Field');
    userEvent.click(input);
    userEvent.tab();

    expect(mockHandleBlur).toHaveBeenCalled();
  });
});

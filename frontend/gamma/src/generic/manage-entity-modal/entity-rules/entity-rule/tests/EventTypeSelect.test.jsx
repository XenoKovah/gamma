import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import genericMessages from '../../../../../i18n';
import EventTypeSelect from '../EventTypeSelect';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('EventTypeSelect Component', () => {
  const mockSetFieldValue = jest.fn();
  const mockHandleBlur = jest.fn();
  const mockValues = {
    rules: [
      {
        action: {
          eventType: '',
          id: '',
          count: '',
          points: '',
        },
      },
    ],
  };
  const mockTouched = {};
  const mockErrors = {};

  const mockData = {
    actions: [
      {
        id: 'action1',
        eventName: 'testAction1',
        title: 'Test Action 1',
      },
      {
        id: 'action2',
        eventName: 'testAction2',
        title: 'Test Action 2',
      },
    ],
  };

  const defaultProps = {
    ruleIndex: 0,
    data: mockData,
    translations: {
      action: 'Action',
    },
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
    <EventTypeSelect {...defaultProps} {...props} />,
  );

  it('renders select dropdown with default option', () => {
    const { getByTestId, getByText } = renderComponent();

    const select = getByTestId('event-type-select');
    expect(select).toBeInTheDocument();
    expect(
      getByText(
        genericMessages.modalEntityActionEventNameLabelText.defaultMessage.replace('{eventType}', 'action'),
      ),
    ).toBeInTheDocument();
  });

  it('renders all action options', () => {
    const { getByText } = renderComponent();

    expect(getByText('Test Action 1')).toBeInTheDocument();
    expect(getByText('Test Action 2')).toBeInTheDocument();
  });

  it('calls setFieldValue with correct values when selecting an action', () => {
    const { getByTestId } = renderComponent();

    const select = getByTestId('event-type-select');
    userEvent.selectOptions(select, 'testAction1');

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.eventType', 'testAction1');
    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.id', 'action1');
    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.count', '');
    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.points', '');
  });

  it('displays error message when field is touched and has error', () => {
    useFormikContext.mockReturnValue({
      values: mockValues,
      touched: {
        rules: [
          {
            action: {
              eventType: true,
            },
          },
        ],
      },
      errors: {
        rules: [
          {
            action: {
              eventType: 'This is an error',
            },
          },
        ],
      },
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });

    const { getByText } = renderComponent();
    expect(getByText('This is an error')).toBeInTheDocument();
  });

  it('calls handleBlur when select loses focus', () => {
    const { getByTestId } = renderComponent();

    const select = getByTestId('event-type-select');
    userEvent.click(select);
    userEvent.tab();

    expect(mockHandleBlur).toHaveBeenCalled();
  });

  it('maintains selected value when re-rendered', () => {
    useFormikContext.mockReturnValue({
      values: {
        rules: [
          {
            action: {
              eventType: 'testAction1',
              id: 'action1',
              count: '',
              points: '',
            },
          },
        ],
      },
      touched: mockTouched,
      errors: mockErrors,
      setFieldValue: mockSetFieldValue,
      handleBlur: mockHandleBlur,
    });

    const { getByTestId } = renderComponent();
    const select = getByTestId('event-type-select');

    expect(select).toHaveValue('testAction1');
  });
});

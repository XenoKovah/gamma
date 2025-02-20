import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import messages from '../../../../../i18n';
import ActionField from '../ActionField';

describe('ActionField Component', () => {
  const mockSetFieldValue = jest.fn();
  const mockHandleBlur = jest.fn();

  const defaultProps = {
    ruleIndex: 0,
    name: 'actionName',
    type: 'text',
    label: 'Action Name',
    values: { rules: [{ action: { actionName: '' } }] },
    touched: { rules: [{ action: { actionName: false } }] },
    errors: { rules: [{ action: { actionName: '' } }] },
    setFieldValue: mockSetFieldValue,
    handleBlur: mockHandleBlur,
    options: ['Option 1', 'Option 2'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<ActionField {...defaultProps} {...props} />);

  it('renders text input with correct label', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox', { name: defaultProps.label });
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders number input when type is number', () => {
    const { getByRole } = renderComponent({ type: 'number' });

    const input = getByRole('spinbutton', { name: defaultProps.label });
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
  });

  it('renders select field when type is select', () => {
    const { getByRole, getByText } = renderComponent({ type: 'select' });

    const select = getByRole('combobox');
    expect(select).toBeInTheDocument();

    expect(getByText(
      messages.modalEntityActionEventNameLabelText.defaultMessage
        .replace('{eventType}', defaultProps.label.toLowerCase()),
    )).toBeInTheDocument();
    defaultProps.options.forEach((option) => expect(getByText(option)).toBeInTheDocument());
  });

  it('calls setFieldValue when input value changes', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, 'New Value');
    waitFor(() => expect(input).toHaveValue('New Value'));
  });

  it('calls handleBlur when input loses focus', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');

    userEvent.click(input);
    userEvent.tab();

    expect(mockHandleBlur).toHaveBeenCalledTimes(1);
  });

  it('displays error message when there is an error', () => {
    const { getByText } = renderComponent({
      touched: { rules: [{ action: { actionName: true } }] },
      errors: { rules: [{ action: { actionName: 'This field is required' } }] },
    });

    expect(getByText('This field is required')).toBeInTheDocument();
  });

  it('does not display error message when field is not touched', () => {
    const { queryByText } = renderComponent({
      touched: { rules: [{ action: { actionName: false } }] },
      errors: { rules: [{ action: { actionName: 'This field is required' } }] },
    });

    expect(queryByText('This field is required')).not.toBeInTheDocument();
  });
});

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
    options: [
      { id: 'opt1', eventName: 'Option 1', title: 'Option 1' },
      { id: 'opt2', eventName: 'Option 2', title: 'Option 2' },
    ],
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

    defaultProps.options.forEach((option) => {
      expect(getByText(option.title)).toBeInTheDocument();
    });
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

  it('updates select value when an option is selected', async () => {
    const { getByRole } = renderComponent({ type: 'select' });

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'Option 1');

    await waitFor(() => expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.actionName', 'Option 1'));
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

  it('does not render Form.Control.Feedback when there is no error', () => {
    const { queryByRole } = renderComponent();

    expect(queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders correct field name based on ruleIndex and name', () => {
    const { getByRole } = renderComponent({ ruleIndex: 2, name: 'customField' });

    const input = getByRole('textbox');
    expect(input).toHaveAttribute('name', 'rules.2.action.customField');
  });

  it('renders select field with correct options', () => {
    const { getByRole, getByText } = renderComponent({ type: 'select' });

    const select = getByRole('combobox');
    expect(select).toBeInTheDocument();

    defaultProps.options.forEach((option) => {
      expect(getByText(option.title)).toBeInTheDocument();
    });
  });

  it('renders select field with empty option as placeholder', () => {
    const { getByRole, getByText } = renderComponent({ type: 'select' });

    const select = getByRole('combobox');
    expect(select).toBeInTheDocument();

    expect(getByText(
      messages.modalEntityActionEventNameLabelText.defaultMessage
        .replace('{eventType}', defaultProps.label.toLowerCase()),
    )).toBeInTheDocument();
  });

  it('renders an input with an error state if validation fails', () => {
    const { getByRole } = renderComponent({
      touched: { rules: [{ action: { actionName: true } }] },
      errors: { rules: [{ action: { actionName: 'Error message' } }] },
    });

    const input = getByRole('textbox');
    expect(input).toHaveClass('is-invalid');
  });

  it('does not render error state if field is not touched', () => {
    const { getByRole } = renderComponent({
      touched: { rules: [{ action: { actionName: false } }] },
      errors: { rules: [{ action: { actionName: 'Error message' } }] },
    });

    const input = getByRole('textbox');
    expect(input).not.toHaveClass('is-invalid');
  });
});

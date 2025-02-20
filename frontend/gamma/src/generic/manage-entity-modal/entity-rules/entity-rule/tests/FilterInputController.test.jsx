import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import { useTranslate } from '../../../../../i18n/utils';
import messages from '../../../../../i18n/en';
import FilterInputController from '../FilterInputController';

jest.mock('../../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('FilterInputController', () => {
  const mockSetFieldValue = jest.fn();
  const mockSetTouched = jest.fn();

  const translations = {
    'generic.modal.entity.rules.filter.select.title': messages['generic.modal.entity.rules.filter.select.title'].defaultMessage,
  };

  const defaultProps = {
    ruleIndex: 0,
    name: 'testField',
    type: 'text',
    as: 'input',
    label: 'Test Label',
    filterKey: 'testFilter',
    placeholder: 'Select a filter',
    rule: {
      filters: {
        testFilter: '',
      },
    },
    options: ['Option 1', 'Option 2'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      setFieldValue: mockSetFieldValue,
      setTouched: mockSetTouched,
      touched: { rules: [{ filters: {} }] },
      errors: { rules: [{ filters: {} }] },
    });

    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<FilterInputController {...defaultProps} {...props} />);

  it('renders input field with correct attributes', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('name', defaultProps.name);
    expect(input).toHaveAttribute('placeholder', defaultProps.placeholder);
  });

  it("renders number input when type is 'number'", () => {
    const { getByRole } = renderComponent({ type: 'number', as: 'input' });

    const input = getByRole('spinbutton');
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('type', 'number');
  });

  it("renders select field with options when 'as' is 'select'", () => {
    const { getByRole, getByText } = renderComponent({ as: 'select', type: undefined });

    const select = getByRole('combobox');
    expect(select).toBeInTheDocument();

    expect(getByText(translations['generic.modal.entity.rules.filter.select.title'])).toBeInTheDocument();
    expect(getByText('Option 1')).toBeInTheDocument();
    expect(getByText('Option 2')).toBeInTheDocument();
  });

  it('calls setFieldValue when input value changes', () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');
    userEvent.type(input, 'New Value');

    waitFor(() => expect(input).toHaveValue('New Value'));
  });

  it('calls setTouched when input loses focus', async () => {
    const { getByRole } = renderComponent();

    const input = getByRole('textbox');

    userEvent.click(input);
    userEvent.tab();

    expect(mockSetTouched).toHaveBeenCalled();
  });

  it('displays validation error when input is touched and has an error', () => {
    const { getByText } = renderComponent({
      touched: { rules: [{ filters: { testFilter: true } }] },
      errors: { rules: [{ filters: { testFilter: 'Required field' } }] },
    });

    waitFor(() => {
      expect(getByText('Required field')).toBeInTheDocument();
    });
  });

  it('does not display error message when field is not touched', () => {
    const { queryByText } = renderComponent({
      touched: { rules: [{ filters: { testFilter: false } }] },
      errors: { rules: [{ filters: { testFilter: 'Required field' } }] },
    });

    expect(queryByText('Required field')).not.toBeInTheDocument();
  });
});

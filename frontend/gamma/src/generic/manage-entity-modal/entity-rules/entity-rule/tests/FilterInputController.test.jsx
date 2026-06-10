import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import messages from '../../../../../i18n';
import FilterInputController from '../FilterInputController';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('FilterInputController', () => {
  const mockSetFieldValue = jest.fn();
  const mockSetTouched = jest.fn();

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

    expect(
      getByText(
        messages.modalEntityRulesFilterSelectTitle.defaultMessage.replace('{filterName}', defaultProps.placeholder),
      ),
    ).toBeInTheDocument();
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

describe('FilterInputController free-text multi mode (blocks)', () => {
  const mockSetFieldValue = jest.fn();
  const mockSetTouched = jest.fn();

  const BLOCK_A = 'block-v1:org+C1+1+type@done+block@aaaa';
  const BLOCK_B = 'block-v1:org+C1+1+type@done+block@bbbb';
  const BLOCK_C = 'block-v1:org+C1+1+type@done+block@cccc';

  const blocksProps = {
    ruleIndex: 0,
    filterKey: 'blocks',
    label: 'Blocks',
    placeholder: 'Blocks',
    multiple: true,
    freeText: true,
    rule: {
      filters: { blocks: '' },
      action: { count: '' },
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      setFieldValue: mockSetFieldValue,
      setTouched: mockSetTouched,
      touched: { rules: [{ filters: {} }] },
      errors: { rules: [{ filters: {} }] },
    });
  });

  afterEach(cleanup);

  const addButtonText = messages.modalEntityRulesBtnAddFilterText.defaultMessage;
  const removeButtonText = messages.modalEntityRulesBtnRemoveFilterText.defaultMessage;

  it('adds a pasted usage key as a list entry and syncs the action count', () => {
    const { getByRole, getByText } = renderWithProviders(<FilterInputController {...blocksProps} />);

    userEvent.type(getByRole('textbox'), BLOCK_A);
    userEvent.click(getByText(addButtonText));

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.blocks', [BLOCK_A]);
    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.count', 1);
  });

  it('adds an entry on Enter without submitting and clears the input', () => {
    const { getByRole } = renderWithProviders(<FilterInputController {...blocksProps} />);

    const input = getByRole('textbox');
    userEvent.type(input, `${BLOCK_B}{enter}`);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.blocks', [BLOCK_B]);
    expect(input).toHaveValue('');
  });

  it('renders existing entries as removable rows and resyncs the count on removal', () => {
    const props = {
      ...blocksProps,
      rule: { filters: { blocks: [BLOCK_A, BLOCK_B] }, action: { count: 2 } },
    };
    const { getAllByText, getByTitle } = renderWithProviders(<FilterInputController {...props} />);

    expect(getByTitle(BLOCK_A)).toBeInTheDocument();
    expect(getByTitle(BLOCK_B)).toBeInTheDocument();

    userEvent.click(getAllByText(removeButtonText)[0]);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.blocks', [BLOCK_B]);
    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.action.count', 1);
  });

  it('does not touch a count the admin has deliberately diverged (any-N-of-M rule)', () => {
    const props = {
      ...blocksProps,
      rule: { filters: { blocks: [BLOCK_A, BLOCK_B] }, action: { count: 1 } },
    };
    const { getByRole, getByText } = renderWithProviders(<FilterInputController {...props} />);

    userEvent.type(getByRole('textbox'), BLOCK_C);
    userEvent.click(getByText(addButtonText));

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.blocks', [BLOCK_A, BLOCK_B, BLOCK_C]);
    const countCalls = mockSetFieldValue.mock.calls.filter(([field]) => field === 'rules.0.action.count');
    expect(countCalls).toHaveLength(0);
  });

  it('ignores duplicate and empty entries', () => {
    const props = {
      ...blocksProps,
      rule: { filters: { blocks: [BLOCK_A] }, action: { count: 1 } },
    };
    const { getByRole, getByText } = renderWithProviders(<FilterInputController {...props} />);

    userEvent.type(getByRole('textbox'), BLOCK_A);
    userEvent.click(getByText(addButtonText));
    userEvent.click(getByText(addButtonText));

    const blockCalls = mockSetFieldValue.mock.calls.filter(([field]) => field === 'rules.0.filters.blocks');
    expect(blockCalls).toHaveLength(0);
  });
});

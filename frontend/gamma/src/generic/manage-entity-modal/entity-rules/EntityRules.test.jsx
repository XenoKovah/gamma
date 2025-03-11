import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../setupTests';
import messages from '../../../i18n';
import EntityRule from './entity-rule';
import EntityRules from '.';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

jest.mock('./entity-rule', () => jest.fn(() => <div data-testid="entity-rule" />));

describe('EntityRules', () => {
  const mockSetFieldValue = jest.fn();
  const rulesContainerRef = { current: document.createElement('div') };
  const lastRuleRef = { current: document.createElement('div') };

  const defaultProps = {
    rulesContainerRef,
    lastRuleRef,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    rulesContainerRef.current = document.createElement('div');
    lastRuleRef.current = document.createElement('div');
    useFormikContext.mockReturnValue({
      values: { rules: [] },
      setFieldValue: mockSetFieldValue,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<EntityRules {...defaultProps} {...props} />);

  it('renders heading', () => {
    const { getByText } = renderComponent();
    expect(getByText(messages.modalEntityRulesTitle.defaultMessage)).toBeInTheDocument();
  });

  it('renders an alert when no rules exist', () => {
    const { getByText } = renderComponent();
    expect(getByText(messages.modalEntityRulesAlertNoRulesTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.modalEntityRulesAlertNoRulesDescription.defaultMessage)).toBeInTheDocument();
  });

  it('renders rules when they exist', () => {
    useFormikContext.mockReturnValue({
      values: { rules: [{ tempId: '1' }] },
      setFieldValue: mockSetFieldValue,
    });

    const { getByTestId } = renderComponent();
    expect(getByTestId('entity-rule')).toBeInTheDocument();
  });

  it('calls setFieldValue when adding a new rule', () => {
    useFormikContext.mockReturnValue({
      values: { rules: [] },
      setFieldValue: mockSetFieldValue,
    });

    const { getByRole } = renderComponent();
    const addButton = getByRole('button', {
      name: messages.modalEntityRulesAddNewRuleBtnText.defaultMessage,
    });

    userEvent.click(addButton);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules', expect.any(Array));
  });

  it('calls setFieldValue when removing a rule', () => {
    useFormikContext.mockReturnValue({
      values: { rules: [{ tempId: '1' }, { tempId: '2' }] },
      setFieldValue: mockSetFieldValue,
    });

    EntityRule.mockImplementation(({ removeRule, ruleIndex }) => (
      <button data-testid="remove-rule-btn" type="button" onClick={() => removeRule(ruleIndex)}>
        {messages.modalEntityRulesBtnDeleteText.defaultMessage}
      </button>
    ));

    const { getAllByTestId } = renderComponent();

    const removeButtons = getAllByTestId('remove-rule-btn');
    userEvent.click(removeButtons[0]);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules', expect.any(Array));
  });

  it('adds a new rule with correct structure when add button is clicked', () => {
    useFormikContext.mockReturnValue({
      values: { rules: [] },
      setFieldValue: mockSetFieldValue,
    });

    const { getByRole } = renderComponent();
    const addButton = getByRole('button', {
      name: messages.modalEntityRulesAddNewRuleBtnText.defaultMessage,
    });

    userEvent.click(addButton);

    expect(mockSetFieldValue).toHaveBeenCalledWith(
      'rules',
      expect.arrayContaining([
        expect.objectContaining({
          action: {},
          filters: {},
        }),
      ]),
    );
  });

  it('removes the correct rule when remove button is clicked', () => {
    useFormikContext.mockReturnValue({
      values: { rules: [{ tempId: '1' }, { tempId: '2' }] },
      setFieldValue: mockSetFieldValue,
    });

    EntityRule.mockImplementation(({ removeRule, ruleIndex }) => (
      <button data-testid="remove-rule-btn" type="button" onClick={() => removeRule(ruleIndex)}>
        {messages.modalEntityRulesBtnDeleteText.defaultMessage}
      </button>
    ));

    const { getAllByTestId } = renderComponent();

    const removeButtons = getAllByTestId('remove-rule-btn');
    userEvent.click(removeButtons[1]);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules', [{ tempId: '1' }]);
  });

  it('scrolls to the last rule when a new rule is added', async () => {
    lastRuleRef.current.scrollIntoView = jest.fn();

    useFormikContext.mockReturnValue({
      values: { rules: [] },
      setFieldValue: mockSetFieldValue,
    });

    const { getByRole } = renderComponent();
    const addButton = getByRole('button', {
      name: messages.modalEntityRulesAddNewRuleBtnText.defaultMessage,
    });

    userEvent.click(addButton);

    await waitFor(() => {
      expect(lastRuleRef.current.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' });
    });
  });
});

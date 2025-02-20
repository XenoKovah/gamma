import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../setupTests';
import { useTranslate } from '../../../i18n/utils';
import messages from '../../../i18n/en';
import EntityRule from './entity-rule';
import EntityRules from '.';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

jest.mock('../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

jest.mock('./entity-rule', () => jest.fn(() => <div data-testid="entity-rule" />));

describe('EntityRules', () => {
  const mockSetFieldValue = jest.fn();
  const rulesContainerRef = { current: document.createElement('div') };
  const lastRuleRef = { current: document.createElement('div') };

  const translations = {
    'generic.modal.entity.rules.heading': messages['generic.modal.entity.rules.heading'].defaultMessage,
    'generic.modal.entity.rules.alert.no-rules.heading': messages['generic.modal.entity.rules.alert.no-rules.heading'].defaultMessage,
    'generic.modal.entity.rules.alert.no-rules.description': messages['generic.modal.entity.rules.alert.no-rules.description'].defaultMessage,
    'generic.modal.entity.rules.button.add-new-rule.text': messages['generic.modal.entity.rules.button.add-new-rule.text'].defaultMessage,
    'generic.modal.entity.rules.button.delete.text': messages['generic.modal.entity.rules.button.delete.text'].defaultMessage,
  };

  const defaultProps = {
    rulesContainerRef,
    lastRuleRef,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      values: { rules: [] },
      setFieldValue: mockSetFieldValue,
    });

    useTranslate.mockImplementation((key) => translations[key] || key);
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<EntityRules {...defaultProps} {...props} />);

  it('renders heading', () => {
    const { getByText } = renderComponent();
    expect(getByText(translations['generic.modal.entity.rules.heading'])).toBeInTheDocument();
  });

  it('renders an alert when no rules exist', () => {
    const { getByText } = renderComponent();
    expect(getByText(translations['generic.modal.entity.rules.alert.no-rules.heading'])).toBeInTheDocument();
    expect(getByText(translations['generic.modal.entity.rules.alert.no-rules.description'])).toBeInTheDocument();
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
      name: translations['generic.modal.entity.rules.button.add-new-rule.text'],
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
        {translations['generic.modal.entity.rules.button.delete.text']}
      </button>
    ));

    const { getAllByTestId } = renderComponent();

    const removeButtons = getAllByTestId('remove-rule-btn');
    userEvent.click(removeButtons[0]);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules', expect.any(Array));
  });
});

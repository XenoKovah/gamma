import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import userEvent from '@testing-library/user-event';
import { useFormikContext } from 'formik';

import genericMessages from '../../../../../i18n';
import { renderWithProviders } from '../../../../../setupTests';
import EntityRule from '..';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('EntityRule', () => {
  const mockSetFieldValue = jest.fn();
  const mockHandleBlur = jest.fn();
  const mockRemoveRule = jest.fn();

  const defaultProps = {
    ruleIndex: 0,
    removeRule: mockRemoveRule,
    rule: {
      filters: {
        org: 'test-org',
      },
    },
    data: {
      courses: ['Course 1', 'Course 2'],
      organizations: ['Org 1', 'Org 2'],
      actions: [{ eventType: 'view' }, { eventType: 'complete' }],
    },
    hasFilters: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      values: { rules: [defaultProps.rule] },
      touched: { rules: [{ filters: {} }] },
      handleBlur: mockHandleBlur,
      errors: { rules: [{ filters: {} }] },
      setFieldValue: mockSetFieldValue,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<EntityRule {...defaultProps} {...props} />);

  it('renders rule title and action section', () => {
    const { getByText } = renderComponent();

    expect(getByText(genericMessages.modalEntityRulesRuleTitle.defaultMessage.replace('{id}', 1))).toBeInTheDocument();
    expect(getByText(genericMessages.modalEntityRulesActionHeadingTitle.defaultMessage)).toBeInTheDocument();
  });

  // TODO: Fix this test
  it.skip('renders action fields based on available actions', () => {
    const { getByLabelText } = renderComponent();

    expect(getByLabelText(genericMessages.modalEntityRulesRuleEventTypeLabel.defaultMessage)).toBeInTheDocument();
    expect(getByLabelText(genericMessages.modalEntityRulesRuleCountLabel.defaultMessage)).toBeInTheDocument();
  });

  it('removes a filter when remove filter button is clicked', () => {
    const { getByRole } = renderComponent();

    const removeFilterButton = getByRole('button', {
      name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage,
    });
    userEvent.click(removeFilterButton);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters', {});
  });

  it('calls removeRule when delete rule button is clicked', () => {
    const { getByRole } = renderComponent();

    const deleteRuleButton = getByRole('button', {
      name: genericMessages.modalEntityRulesBtnDeleteText.defaultMessage,
    });
    userEvent.click(deleteRuleButton);

    expect(mockRemoveRule).toHaveBeenCalledWith(0);
  });

  it('renders SelectFilters when there are available filters', () => {
    const { getByTestId } = renderComponent();

    expect(getByTestId('add-filter-select')).toBeInTheDocument();
  });

  it('removes filter correctly from state when remove filter button is clicked', () => {
    const { getByRole } = renderComponent();

    const removeFilterButton = getByRole('button', {
      name: genericMessages.modalEntityRulesBtnRemoveFilterText.defaultMessage,
    });

    userEvent.click(removeFilterButton);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters', {});
  });

  it('renders IntervalDatePicker when interval filter is present', () => {
    const { getByLabelText } = renderComponent({
      rule: {
        filters: {
          interval: { start: '2024-01-01', end: '2024-01-10' },
        },
      },
    });

    expect(getByLabelText(
      genericMessages.modalEntityRulesIntervalStartLabelText.defaultMessage,
    )).toBeInTheDocument();
    expect(getByLabelText(
      genericMessages.modalEntityRulesIntervalEndLabelText.defaultMessage,
    )).toBeInTheDocument();
  });

  it('renders the heading when filters are present', () => {
    const { getByRole } = renderComponent();

    expect(getByRole('heading', {
      name: genericMessages.modalEntityRulesFiltersHeadingTitle.defaultMessage,
    })).toBeInTheDocument();
  });

  it('does not render the heading when filters are absent', () => {
    const { queryByRole } = renderComponent({ hasFilters: false });

    expect(queryByRole('heading', {
      name: genericMessages.modalEntityRulesFiltersHeadingTitle.defaultMessage,
    })).not.toBeInTheDocument();
  });
});

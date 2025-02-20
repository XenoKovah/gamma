import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import userEvent from '@testing-library/user-event';
import { useFormikContext } from 'formik';

import { useTranslate } from '../../../../../i18n/utils';
import messages from '../../../../../i18n/en';
import { renderWithProviders } from '../../../../../setupTests';
import EntityRule from '..';

jest.mock('../../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('EntityRule', () => {
  const mockSetFieldValue = jest.fn();
  const mockHandleBlur = jest.fn();
  const mockRemoveRule = jest.fn();

  const translations = {
    'generic.modal.entity.rules.rule.heading': messages['generic.modal.entity.rules.rule.heading'].defaultMessage,
    'generic.modal.entity.rules.action.heading.text': messages['generic.modal.entity.rules.action.heading.text'].defaultMessage,
    'generic.modal.entity.rules.filters.heading.text': messages['generic.modal.entity.rules.filters.heading.text'].defaultMessage,

    'generic.modal.entity.rules.rule.event-type.label': messages['generic.modal.entity.rules.rule.event-type.label'].defaultMessage,
    'generic.modal.entity.rules.rule.count.label': messages['generic.modal.entity.rules.rule.count.label'].defaultMessage,
    'generic.modal.entity.rules.rule.course.label': messages['generic.modal.entity.rules.rule.course.label'].defaultMessage,
    'generic.modal.entity.action.event.name.label': messages['generic.modal.entity.action.event.name.label'].defaultMessage,
    'generic.modal.entity.rules.button.remove-filter.text': messages['generic.modal.entity.rules.button.remove-filter.text'].defaultMessage,
    'generic.modal.entity.rules.button.delete.text': messages['generic.modal.entity.rules.button.delete.text'].defaultMessage,
    'generic.modal.entity.rules.filters.select.title': messages['generic.modal.entity.rules.filters.select.title'].defaultMessage,
  };

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

    useTranslate.mockImplementation((key, values) => (key === 'generic.modal.entity.rules.rule.heading'
      ? translations[key].replace('{id}', values?.id || 0)
      : translations[key] || key));
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<EntityRule {...defaultProps} {...props} />);

  it('renders rule title and action section', () => {
    const { getByText } = renderComponent();

    expect(getByText(translations['generic.modal.entity.rules.rule.heading'].replace('{id}', 1))).toBeInTheDocument();
    expect(getByText(translations['generic.modal.entity.rules.action.heading.text'])).toBeInTheDocument();
  });

  it('renders action fields based on available actions', () => {
    const { getByLabelText } = renderComponent();

    expect(getByLabelText(translations['generic.modal.entity.rules.rule.event-type.label'])).toBeInTheDocument();
    expect(getByLabelText(translations['generic.modal.entity.rules.rule.count.label'])).toBeInTheDocument();
  });

  it('removes a filter when remove filter button is clicked', () => {
    const { getByRole } = renderComponent();

    const removeFilterButton = getByRole('button', {
      name: translations['generic.modal.entity.rules.button.remove-filter.text'],
    });
    userEvent.click(removeFilterButton);

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters', {});
  });

  it('calls removeRule when delete rule button is clicked', () => {
    const { getByRole } = renderComponent();

    const deleteRuleButton = getByRole('button', {
      name: translations['generic.modal.entity.rules.button.delete.text'],
    });
    userEvent.click(deleteRuleButton);

    expect(mockRemoveRule).toHaveBeenCalledWith(0);
  });
});

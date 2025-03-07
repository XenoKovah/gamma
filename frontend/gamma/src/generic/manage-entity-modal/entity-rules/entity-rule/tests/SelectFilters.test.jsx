import React from 'react';
import { cleanup, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import { useFormikContext } from 'formik';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import messages from '../../../../../i18n';
import SelectFilters from '../SelectFilters';

jest.mock('formik', () => ({
  useFormikContext: jest.fn(),
}));

describe('SelectFilters Component', () => {
  const mockSetFieldValue = jest.fn();
  const mockValidateForm = jest.fn();
  const filterRefs = { current: {} };
  const startDateRef = { current: { input: { focus: jest.fn() } } };

  const defaultProps = {
    rule: {
      filters: {
        existingFilter: 'some value',
      },
    },
    ruleIndex: 0,
    filterRefs,
    startDateRef,
    AVAILABLE_FILTERS: ['interval', 'org', 'newFilter'],
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useFormikContext.mockReturnValue({
      setFieldValue: mockSetFieldValue,
      validateForm: mockValidateForm,
    });
  });

  afterEach(cleanup);

  const renderComponent = (props = {}) => renderWithProviders(<SelectFilters {...defaultProps} {...props} />);

  it('renders select dropdown with available filters', () => {
    const { getByRole, getByText } = renderComponent();

    const select = getByRole('combobox');
    expect(select).toBeInTheDocument();

    expect(getByText(messages.modalEntityRulesFiltersSelectTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.modalEntityOrganizationFilterTitle.defaultMessage)).toBeInTheDocument();
  });

  it('does not show already selected filters', () => {
    const { queryByText } = renderComponent();

    expect(queryByText('existingFilter')).not.toBeInTheDocument();
  });

  it('calls setFieldValue and validateForm when selecting a filter', () => {
    const { getByRole } = renderComponent();

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'newFilter');

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.newFilter', '');
    expect(mockValidateForm).toHaveBeenCalled();
  });

  it('sets filterRefs correctly and focuses on the new field', () => {
    filterRefs.current.newFilter = { current: { focus: jest.fn() } };

    const { getByRole } = renderComponent();

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'newFilter');
    waitFor(() => expect(filterRefs.current.newFilter.current.focus).toHaveBeenCalled());
  });

  it("focuses on start date field when selecting 'interval' filter", () => {
    const { getByRole } = renderComponent();

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'interval');

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.interval', { start: null, end: null });
    waitFor(() => {
      expect(startDateRef.current.input.focus).toHaveBeenCalled();
    });
  });

  it("focuses on start date field when selecting 'interval' filter", async () => {
    const { getByRole } = renderComponent();

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'interval');

    expect(mockSetFieldValue).toHaveBeenCalledWith('rules.0.filters.interval', { start: null, end: null });
    await waitFor(() => {
      expect(startDateRef.current.input.focus).toHaveBeenCalled();
    });
  });

  it('does not add duplicate filters', () => {
    const { getByRole } = renderComponent({
      rule: {
        filters: {
          existingFilter: 'some value',
          newFilter: 'already exists',
        },
      },
    });

    const select = getByRole('combobox');
    userEvent.selectOptions(select, 'Interval');

    expect(mockSetFieldValue).not.toHaveBeenCalledWith('rules.0.filters.interval', '');
  });

  it('does not call setFieldValue when selecting empty option', () => {
    const { getByRole } = renderComponent();

    const select = getByRole('combobox');
    userEvent.selectOptions(select, '');

    expect(mockSetFieldValue).not.toHaveBeenCalled();
  });
});

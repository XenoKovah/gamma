import React from 'react';
import { cleanup, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import { renderWithProviders } from '../../../../setupTests';
import { useTranslate } from '../../../../i18n/utils';
import messages from '../../i18n/en';
import SubHeader from '.';

jest.mock('../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('SubHeader', () => {
  afterEach(cleanup);

  const translations = {
    'modules.badges.heading.text': messages['modules.badges.heading.text'].defaultMessage,
    'modules.badges.total-badges.counter.text':
      messages['modules.badges.total-badges.counter.text'].defaultMessage,
    'modules.badges.button.add-badge': messages['modules.badges.button.add-badge'].defaultMessage,
    'modules.badges.modal.add-badge.title': messages['modules.badges.modal.add-badge.title'].defaultMessage,
  };

  beforeEach(() => {
    useTranslate.mockImplementation((key, values) => (key === 'modules.badges.total-badges.counter.text'
      ? translations[key].replace('{badgesCount}', values?.badgesCount || 0)
      : translations[key] || key));
  });

  const renderSubHeader = (props = {}) => renderWithProviders(<SubHeader {...props} />);

  it('renders heading, "Add badge" button, and total badges count (default 0)', () => {
    const { getByRole, getByText } = renderSubHeader({
      isError: false, badgesCount: 0, openManageEntityModal: jest.fn(),
    });

    expect(getByRole('heading', { level: 1 }))
      .toHaveTextContent(translations['modules.badges.heading.text']);
    expect(getByText(
      translations['modules.badges.total-badges.counter.text'].replace('{badgesCount}', 0),
    )).toBeInTheDocument();
    expect(getByRole('button', { name: translations['modules.badges.button.add-badge'] }))
      .toBeInTheDocument();
  });

  it('renders correct badge count when badgesCount is greater than zero', () => {
    const { getByText } = renderSubHeader({
      isError: false, badgesCount: 5, openManageEntityModal: jest.fn(),
    });

    expect(getByText(
      translations['modules.badges.total-badges.counter.text'].replace('{badgesCount}', 5),
    )).toBeInTheDocument();
  });

  it('renders correct badge count when badgesCount is a large number', () => {
    const { getByText } = renderSubHeader({
      isError: false, badgesCount: 999, openManageEntityModal: jest.fn(),
    });

    expect(getByText(
      translations['modules.badges.total-badges.counter.text'].replace('{badgesCount}', 999),
    )).toBeInTheDocument();
  });

  it('does not render "Add badge" button and total badges count when isError is true', () => {
    const {
      queryByText, queryByRole, getByRole,
    } = renderSubHeader({ isError: true, badgesCount: 10, openManageEntityModal: jest.fn() });

    expect(getByRole('heading', { level: 1 }))
      .toHaveTextContent(translations['modules.badges.heading.text']);
    expect(queryByText(
      translations['modules.badges.total-badges.counter.text'].replace('{badgesCount}', 10),
    )).not.toBeInTheDocument();
    expect(queryByRole('button', { name: translations['modules.badges.button.add-badge'] }))
      .not.toBeInTheDocument();
  });

  it('calls openManageEntityModalDialog when "Add badge" button is clicked', () => {
    const mockOpenManageEntityModal = jest.fn();
    const { getByRole } = renderSubHeader({
      isError: false,
      badgesCount: 5,
      openManageEntityModal: mockOpenManageEntityModal,
    });

    const addButton = getByRole('button', { name: translations['modules.badges.button.add-badge'] });
    userEvent.click(addButton);

    expect(mockOpenManageEntityModal).toHaveBeenCalledTimes(1);
    waitFor(() => {
      const ManageEntityModal = getByRole('dialog');
      expect(within(ManageEntityModal).getByText(translations['modules.badges.modal.add-badge.title'])).toBeInTheDocument();
    });
  });
});

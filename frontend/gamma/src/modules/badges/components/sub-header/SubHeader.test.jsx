import React from 'react';
import { cleanup, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import { renderWithProviders } from '../../../../setupTests';
import messages from '../../i18n';
import SubHeader from '.';

describe('SubHeader', () => {
  afterEach(cleanup);

  const renderSubHeader = (props = {}) => renderWithProviders(<SubHeader {...props} />);

  it('renders heading, "Add badge" button, and total badges count (default 0)', () => {
    const { getByRole, getByText } = renderSubHeader({
      isError: false, badgesCount: 0, openManageEntityModal: jest.fn(),
    });

    expect(getByRole('heading', { level: 1 })).toHaveTextContent(messages.pageTitle.defaultMessage);
    expect(getByText(
      messages.totalBadgesCount.defaultMessage.replace('{badgesCount}', 0),
    )).toBeInTheDocument();
    expect(getByRole('button', { name: messages.addBadgeBtnText.defaultMessage })).toBeInTheDocument();
  });

  it('renders correct badge count when badgesCount is greater than zero', () => {
    const { getByText } = renderSubHeader({
      isError: false, badgesCount: 5, openManageEntityModal: jest.fn(),
    });

    expect(getByText(
      messages.totalBadgesCount.defaultMessage.replace('{badgesCount}', 5),
    )).toBeInTheDocument();
  });

  it('renders correct badge count when badgesCount is a large number', () => {
    const { getByText } = renderSubHeader({
      isError: false, badgesCount: 999, openManageEntityModal: jest.fn(),
    });

    expect(getByText(
      messages.totalBadgesCount.defaultMessage.replace('{badgesCount}', 999),
    )).toBeInTheDocument();
  });

  it('does not render "Add badge" button and total badges count when isError is true', () => {
    const {
      queryByText, queryByRole, getByRole,
    } = renderSubHeader({ isError: true, badgesCount: 10, openManageEntityModal: jest.fn() });

    expect(getByRole('heading', { level: 1 })).toHaveTextContent(messages.pageTitle.defaultMessage);
    expect(queryByText(
      messages.totalBadgesCount.defaultMessage.replace('{badgesCount}', 999),
    )).not.toBeInTheDocument();
    expect(queryByRole('button', { name: messages.addBadgeBtnText.defaultMessage })).not.toBeInTheDocument();
  });

  it('calls openManageEntityModalDialog when "Add badge" button is clicked', () => {
    const mockOpenManageEntityModal = jest.fn();
    const { getByRole } = renderSubHeader({
      isError: false,
      badgesCount: 5,
      openManageEntityModal: mockOpenManageEntityModal,
    });

    const addButton = getByRole('button', { name: messages.addBadgeBtnText.defaultMessage });
    userEvent.click(addButton);

    expect(mockOpenManageEntityModal).toHaveBeenCalledTimes(1);
    waitFor(() => {
      const ManageEntityModal = getByRole('dialog');
      expect(within(ManageEntityModal).getByText(messages.addManageEntityModalTitle)).toBeInTheDocument();
    });
  });
});

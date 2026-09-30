import React from 'react';
import '@testing-library/jest-dom';
import { cleanup, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../setupTests';
import messages from '../../i18n';
import ExpiryBadgeModal from '.';
import * as data from '../../data';

jest.mock('../../data', () => ({
  fetchBadgeHolders: jest.fn(),
  setBadgeExpiry: jest.fn(),
  expireBadge: jest.fn(),
}));

const HOLDERS = [
  {
    userUid: 'alice', awardedAt: null, expiresAt: '2031-09-29T23:59:59Z', isExpired: false,
  },
  {
    userUid: 'bob', awardedAt: null, expiresAt: null, isExpired: false,
  },
];

describe('ExpiryBadgeModal', () => {
  beforeEach(() => {
    data.fetchBadgeHolders.mockResolvedValue(HOLDERS);
    data.setBadgeExpiry.mockResolvedValue({ updated: ['alice'] });
    data.expireBadge.mockResolvedValue({ updated: ['alice'] });
  });
  afterEach(() => {
    cleanup();
    jest.clearAllMocks();
  });

  const renderModal = () => renderWithProviders(
    <ExpiryBadgeModal isOpen badge={{ id: 7, title: 'Donor' }} onClose={jest.fn()} />,
  );

  it('lists holders with their own expiry dates', async () => {
    const { findByText, getByText } = renderModal();

    expect(await findByText('alice')).toBeInTheDocument();
    expect(getByText('2031-09-29')).toBeInTheDocument();
    expect(getByText('bob')).toBeInTheDocument();
    expect(getByText(messages.expiryNever.defaultMessage)).toBeInTheDocument();
    expect(data.fetchBadgeHolders).toHaveBeenCalledWith(7);
  });

  it('expires only the selected holders immediately', async () => {
    const { findByLabelText, getByRole } = renderModal();

    userEvent.click(await findByLabelText('alice'));
    userEvent.click(getByRole('button', { name: messages.expiryExpireNowBtnText.defaultMessage }));

    await waitFor(() => expect(data.expireBadge).toHaveBeenCalledWith(7, ['alice']));
  });

  it('sets a per-user date for the selected holders', async () => {
    const { findByLabelText, getByTestId, getByRole } = renderModal();

    userEvent.click(await findByLabelText('bob'));
    userEvent.type(getByTestId('expiry-date'), '2036-09-29');
    userEvent.click(getByRole('button', { name: messages.expirySetDateBtnText.defaultMessage }));

    await waitFor(() => expect(data.setBadgeExpiry).toHaveBeenCalledWith(7, ['bob'], '2036-09-29T23:59:59Z'));
  });

  it('makes selected holders permanent with a null expiry', async () => {
    const { findByLabelText, getByRole } = renderModal();

    userEvent.click(await findByLabelText('alice'));
    userEvent.click(getByRole('button', { name: messages.expiryMakePermanentBtnText.defaultMessage }));

    await waitFor(() => expect(data.setBadgeExpiry).toHaveBeenCalledWith(7, ['alice'], null));
  });
});

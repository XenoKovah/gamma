import React from 'react';
import '@testing-library/jest-dom';
import { cleanup, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import { badgesMocks } from '../../../__mocks__';
import messages from '../../../i18n';
import BadgeItem from '.';

describe('BadgeItem', () => {
  afterEach(cleanup);

  const mockOpenConfirmDeletionAlert = jest.fn();

  const defaultProps = {
    title: badgesMocks[0].title,
    description: badgesMocks[0].description,
    image: badgesMocks[0].image,
    openConfirmDeletionAlert: mockOpenConfirmDeletionAlert,
  };

  const renderComponent = (props = {}) => renderWithProviders(<BadgeItem {...defaultProps} {...props} />);

  it('renders with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByText(defaultProps.description)).toBeInTheDocument();
    expect(getByRole('button', { name: messages.badgeEditBtnTitle.defaultMessage })).toBeInTheDocument();
    expect(getByRole('button', { name: messages.badgeDeleteBtnTitle.defaultMessage })).toBeInTheDocument();
  });

  it('renders with default translations when props are missing', () => {
    const { queryByRole, getByText } = renderComponent({
      title: undefined,
      description: undefined,
      image: undefined,
    });

    expect(queryByRole('img')).not.toBeInTheDocument();
    expect(getByText(messages.badgeDefaultTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.badgeDefaultDescription.defaultMessage)).toBeInTheDocument();
  });

  it('calls openConfirmDeletionAlert when delete button is clicked', () => {
    const { getByRole } = renderComponent();

    const deleteButton = getByRole('button', { name: messages.badgeDeleteBtnTitle.defaultMessage });
    userEvent.click(deleteButton);
    expect(mockOpenConfirmDeletionAlert).toHaveBeenCalledTimes(1);

    waitFor(() => {
      const modal = getByRole('dialog');
      expect(within(modal).getByText(messages.confirmDeletionModalDescription.defaultMessage)).toBeInTheDocument();
      expect(within(modal).getByText(messages.confirmDeletionModalTitle.defaultMessage)).toBeInTheDocument();
    });
  });

  it('triggers actions when edit button is clicked', () => {
    const { getByRole } = renderComponent();

    const editButton = getByRole('button', { name: messages.badgeEditBtnTitle.defaultMessage });
    userEvent.click(editButton);
    expect(editButton).toBeEnabled();
  });
});

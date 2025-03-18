import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../../../../setupTests';
import { badgesMocks } from '../../../__mocks__';
import messages from '../../../i18n';
import BadgeItem from '.';

describe('BadgeItem', () => {
  afterEach(cleanup);

  const mockOpenConfirmDeletionAlert = jest.fn();
  const mockHandleOpenManageEntityModal = jest.fn();

  const defaultProps = {
    title: badgesMocks[0].title,
    description: badgesMocks[0].description,
    image: badgesMocks[0].image,
    isActive: true,
    openConfirmDeletionAlert: mockOpenConfirmDeletionAlert,
    handleOpenManageEntityModal: mockHandleOpenManageEntityModal,
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

  it('renders default values when props are missing', () => {
    const { queryByRole, getByText } = renderComponent({ title: undefined, description: undefined, image: undefined });

    expect(queryByRole('img')).not.toBeInTheDocument();
    expect(getByText(messages.badgeDefaultTitle.defaultMessage)).toBeInTheDocument();
    expect(getByText(messages.badgeDefaultDescription.defaultMessage)).toBeInTheDocument();
  });

  it('renders the correct status badge based on isActive prop', () => {
    const { getByText } = renderComponent({ isActive: true });
    expect(getByText(messages.badgeActiveStatusText.defaultMessage)).toBeInTheDocument();

    cleanup();
    renderComponent({ isActive: false });
    expect(getByText(messages.badgeDraftStatusText.defaultMessage)).toBeInTheDocument();
  });

  it('calls openConfirmDeletionAlert when delete button is clicked', async () => {
    const { getByRole } = renderComponent();

    const deleteButton = getByRole('button', { name: messages.badgeDeleteBtnTitle.defaultMessage });
    userEvent.click(deleteButton);
    expect(mockOpenConfirmDeletionAlert).toHaveBeenCalledTimes(1);
  });

  it('calls handleOpenManageEntityModal when edit button is clicked', () => {
    const { getByRole } = renderComponent();

    const editButton = getByRole('button', { name: messages.badgeEditBtnTitle.defaultMessage });
    userEvent.click(editButton);
    expect(mockHandleOpenManageEntityModal).toHaveBeenCalledTimes(1);
  });

  it('renders without an image when none is provided', () => {
    const { queryByRole } = renderComponent({ image: null });
    expect(queryByRole('img')).not.toBeInTheDocument();
  });

  it('renders image with correct alt text when title is provided', () => {
    const { getByRole } = renderComponent();
    const img = getByRole('img', { name: defaultProps.title });
    expect(img).toHaveAttribute('src', defaultProps.image);
  });

  it('renders default alt text when title is missing', () => {
    const { getByRole } = renderComponent({ title: undefined });
    const img = getByRole('img', { name: messages.badgeDefaultTitle.defaultMessage });
    expect(img).toBeInTheDocument();
  });
});

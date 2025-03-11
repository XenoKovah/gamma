import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { useAvatarsContext } from '../../../context/AvatarsContext';
import { useAvatarSets } from '../../../hooks/useAvatarSets';
import { renderWithProviders } from '../../../../../setupTests';
import { avatarSetsMocks } from '../../../__mocks__';
import messages from '../../../i18n';
import AvatarSetItem from '.';

jest.mock('../../../hooks/useAvatarSets', () => ({
  useAvatarSets: jest.fn(),
}));

jest.mock('../../../context/AvatarsContext', () => ({
  useAvatarsContext: jest.fn(),
}));

describe('AvatarSetItem', () => {
  let mockSetCurrentAvatarSetData;

  beforeEach(() => {
    useAvatarSets.mockReturnValue({});
    mockSetCurrentAvatarSetData = jest.fn();

    useAvatarsContext.mockReturnValue({
      setCurrentAvatarSetData: mockSetCurrentAvatarSetData,
    });
  });

  afterEach(cleanup);

  const defaultProps = {
    openConfirmDeletionModal: jest.fn(),
    openManageAvatarSetModal: jest.fn(),
    avatarSetData: avatarSetsMocks[1],
  };

  const renderComponent = (props = {}) => renderWithProviders(<AvatarSetItem {...defaultProps} {...props} />);

  it('renders avatar set card with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.avatarSetData.title })).toBeInTheDocument();
    expect(getByText(defaultProps.avatarSetData.title)).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarSetEditBtnTitle.defaultMessage })).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarSetDeleteBtnTitle.defaultMessage })).toBeInTheDocument();
  });

  it('renders with default translations and avatar set img when props are missing', () => {
    const { getByRole } = renderComponent({
      avatarSetData: { ...avatarSetsMocks[1], avatars: [] },
    });

    // Image placeholder
    expect(getByRole('img')).toBeInTheDocument();
  });

  it('renders draft badge when isDraft is true', () => {
    const { getByText } = renderComponent({
      avatarSetData: { ...avatarSetsMocks[1], isDraft: true },
    });

    expect(getByText(messages.avatarSetDraftBadgeText.defaultMessage)).toBeInTheDocument();
  });

  it('calls openConfirmDeletionModal with correct id when delete button is clicked', () => {
    const { getByRole } = renderComponent();
    const deleteButton = getByRole('button', { name: messages.avatarSetDeleteBtnTitle.defaultMessage });

    userEvent.click(deleteButton);
    expect(defaultProps.openConfirmDeletionModal).toHaveBeenCalledWith(defaultProps.avatarSetData.id);
  });

  it('calls openManageAvatarSetModal and updates context when edit button is clicked', () => {
    const { getByRole } = renderComponent();
    const editButton = getByRole('button', { name: messages.avatarSetEditBtnTitle.defaultMessage });

    userEvent.click(editButton);
    expect(defaultProps.openManageAvatarSetModal).toHaveBeenCalled();
    expect(mockSetCurrentAvatarSetData).toHaveBeenCalledWith(defaultProps.avatarSetData);
  });

  it('renders with default image when avatar set has no avatars', () => {
    const { getByRole } = renderComponent({
      avatarSetData: { ...avatarSetsMocks[1], avatars: [] },
    });

    expect(getByRole('img')).toHaveAttribute('src', expect.stringContaining('test-file-stub'));
  });

  it('renders the latest avatar as the card image when avatars exist', () => {
    const latestAvatar = { id: 999, image: 'latest-avatar.jpg' };
    const avatarSetData = {
      ...avatarSetsMocks[1],
      avatars: [{ id: 1, image: 'old-avatar.jpg' }, latestAvatar],
    };

    const { getByRole } = renderComponent({ avatarSetData });

    expect(getByRole('img')).toHaveAttribute('src', latestAvatar.image);
  });
});

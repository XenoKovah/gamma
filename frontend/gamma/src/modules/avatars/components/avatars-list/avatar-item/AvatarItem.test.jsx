import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../../../../setupTests';
import { avatarSetsMocks } from '../../../__mocks__';
import messages from '../../../i18n';
import AvatarItem from '.';

describe('AvatarItem', () => {
  afterEach(cleanup);

  const defaultProps = {
    id: 1,
    title: 'Default Avatar',
    openConfirmDeletionModal: jest.fn(),
    avatars: avatarSetsMocks[1].avatar,
  };

  const renderComponent = (props = {}) => renderWithProviders(<AvatarItem {...defaultProps} {...props} />);

  it('renders with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarEditBtnTitle.defaultMessage })).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarDeleteBtnTitle.defaultMessage })).toBeInTheDocument();
  });

  it('renders with default translations and avatar img when props are missing', () => {
    const { getByRole } = renderComponent({
      title: undefined,
      avatars: [],
    });

    // Image placeholder
    expect(getByRole('img')).toBeInTheDocument();
  });
});

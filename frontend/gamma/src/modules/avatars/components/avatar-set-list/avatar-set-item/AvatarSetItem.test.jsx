import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../../../../setupTests';
import { avatarSetsMocks } from '../../../__mocks__';
import messages from '../../../i18n';
import AvatarSetItem from '.';

describe('AvatarSetItem', () => {
  afterEach(cleanup);

  const defaultProps = {
    id: 1,
    title: 'Default avatar set',
    openConfirmDeletionModal: jest.fn(),
    avatars: avatarSetsMocks[1].avatars,
  };

  const renderComponent = (props = {}) => renderWithProviders(<AvatarSetItem {...defaultProps} {...props} />);

  it('renders avatar set card with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarSetEditBtnTitle.defaultMessage })).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarSetDeleteBtnTitle.defaultMessage })).toBeInTheDocument();
  });

  it('renders with default translations and avatar set img when props are missing', () => {
    const { getByRole } = renderComponent({
      title: undefined,
      avatars: [],
    });

    // Image placeholder
    expect(getByRole('img')).toBeInTheDocument();
  });
});

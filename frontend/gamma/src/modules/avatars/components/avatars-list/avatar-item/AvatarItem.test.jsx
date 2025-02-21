import React from 'react';
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../../../../setupTests';
import messages from '../../../i18n';
import AvatarItem from '.';

describe('AvatarItem', () => {
  afterEach(cleanup);

  const defaultProps = {
    title: 'Default Avatar',
    imageSrc: 'https://example.com/avatar.jpg',
  };

  const renderComponent = (props = {}) => renderWithProviders(<AvatarItem {...defaultProps} {...props} />);

  it('renders with provided props', () => {
    const { getByRole, getByText } = renderComponent();

    expect(getByRole('img', { name: defaultProps.title })).toBeInTheDocument();
    expect(getByText(defaultProps.title)).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarEditBtnTitle.defaultMessage })).toBeInTheDocument();
    expect(getByRole('button', { name: messages.avatarDeleteBtnTitle.defaultMessage })).toBeInTheDocument();
  });

  it('renders with default translations when props are missing', () => {
    const { queryByRole } = renderComponent({
      title: undefined,
      imageSrc: undefined,
    });

    expect(queryByRole('img')).not.toBeInTheDocument();
  });
});

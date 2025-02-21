import React from 'react';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';

import { renderWithProviders } from '../../setupTests';
import SubHeader from '.';

const defaultProps = {
  title: 'Test Title',
  btnTitle: 'Click Me',
  description: 'This is a description',
  isError: false,
  onClick: jest.fn(),
};

describe('SubHeader', () => {
  afterEach(cleanup);

  it('renders title correctly', () => {
    const { getByRole } = renderWithProviders(<SubHeader {...defaultProps} />);
    expect(getByRole('heading', { level: 1 })).toHaveTextContent('Test Title');
  });

  it('renders button and description when isError is false', () => {
    const { getByText, getByRole } = renderWithProviders(<SubHeader {...defaultProps} />);
    expect(getByText('This is a description')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Click Me' })).toBeInTheDocument();
  });

  it('does not render button and description when isError is true', () => {
    const { queryByText, queryByRole } = renderWithProviders(<SubHeader {...defaultProps} isError />);
    expect(queryByText('This is a description')).not.toBeInTheDocument();
    expect(queryByRole('button', { name: 'Click Me' })).not.toBeInTheDocument();
  });

  it('calls onClick when button is clicked', () => {
    const { getByRole } = renderWithProviders(<SubHeader {...defaultProps} />);
    const button = getByRole('button', { name: 'Click Me' });
    userEvent.click(button);
    expect(defaultProps.onClick).toHaveBeenCalledTimes(1);
  });
});

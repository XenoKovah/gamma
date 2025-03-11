import React from 'react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../setupTests';
import Card from '.';

describe('Card Component', () => {
  const mockOnPrevBtnClick = jest.fn();
  const mockOnNextBtnClick = jest.fn();

  const defaultProps = {
    id: 1,
    title: 'Test Card',
    src: 'https://via.placeholder.com/150',
    prevBtnTitle: 'Previous',
    nextBtnTitle: 'Next',
    onPrevBtnClick: mockOnPrevBtnClick,
    onNextBtnClick: mockOnNextBtnClick,
  };

  const renderComponent = (props = {}) => renderWithProviders(<Card {...defaultProps} {...props} />);

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(cleanup);

  it('renders the card with correct title and image', () => {
    const { getByTestId, getByText, getByRole } = renderComponent();

    const card = getByTestId(`card-item-${defaultProps.id}`);
    expect(card).toBeInTheDocument();

    expect(getByText(defaultProps.title)).toBeInTheDocument();

    const image = getByRole('img', { name: defaultProps.title });
    expect(image).toHaveAttribute('src', defaultProps.src);
    expect(image).toHaveAttribute('alt', defaultProps.title);
  });

  it('renders previous and next buttons with correct titles', () => {
    const { getByRole } = renderComponent();

    expect(getByRole('button', { name: defaultProps.prevBtnTitle })).toBeInTheDocument();
    expect(getByRole('button', { name: defaultProps.nextBtnTitle })).toBeInTheDocument();
  });

  it('renders the card with correct subtitle', () => {
    const { getByText } = renderComponent({
      subtitle: 'Subtitle text',
    });

    expect(getByText('Subtitle text')).toBeInTheDocument();
  });

  it('renders the card with correct badge', () => {
    const { getByText } = renderComponent({
      badgeText: 'Draft',
    });

    expect(getByText('Draft')).toBeInTheDocument();
  });

  it('renders the card with correct section content', () => {
    const { getByText } = renderComponent({
      section: {
        title: 'Test section title',
        content: (
          <p>Test section content</p>
        ),
      },
    });

    expect(getByText('Test section title')).toBeInTheDocument();
    expect(getByText('Test section content')).toBeInTheDocument();
  });

  it('calls onPrevBtnClick when previous button is clicked', async () => {
    const { getByRole } = renderComponent();

    const prevButton = getByRole('button', { name: defaultProps.prevBtnTitle });
    userEvent.click(prevButton);

    expect(mockOnPrevBtnClick).toHaveBeenCalledTimes(1);
  });

  it('calls onNextBtnClick when next button is clicked', async () => {
    const { getByRole } = renderComponent();

    const nextButton = getByRole('button', { name: defaultProps.nextBtnTitle });
    userEvent.click(nextButton);

    expect(mockOnNextBtnClick).toHaveBeenCalledTimes(1);
  });
});

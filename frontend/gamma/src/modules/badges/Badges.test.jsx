import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import { Badges } from '.';

describe('Badges component', () => {
  it('renders the heading with text "Badges"', () => {
    render(<Badges />);

    const heading = screen.getByRole('heading', { name: /badges/i });
    expect(heading).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Count from '../Count';

describe('Count component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('renders label with translated text', () => {
        render(<Count count={1} onChanged={() => {}} />);
        const сount = screen.getByText(/Count/);
        expect(сount).toBeInTheDocument();
    });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import FilterList from '../FilterList';
import '@testing-library/jest-dom';

describe('FilterList component', () => {
    let mockFilters;

    beforeEach(() => {
        mockFilters = {
            org: 'Test Org',
            course: 'Test Course',
            frequency: 'Test Frequency',
            interval: {
                start: '2023-01-01',
                end: '2023-01-31'
            }
        };
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    afterEach(() => {
        window.gettext.mockRestore();
    });

    it('should render a table with filter data', () => {
        render(<FilterList filters={mockFilters} />);
        const orgCell = screen.getByText(/Test Org/i);
        const courseCell = screen.getByText(/Test Course/i);
        const frequencyCell = screen.getByText(/Test Frequency/i);
        const start = new Date("2023-01-01").toDateString();
        const end = new Date("2023-01-31").toDateString();
        const intervalCell = screen.getByText(`${start} - ${end}`);

        expect(orgCell).toBeInTheDocument();
        expect(courseCell).toBeInTheDocument();
        expect(frequencyCell).toBeInTheDocument();
        expect(intervalCell).toBeInTheDocument();
    });
});

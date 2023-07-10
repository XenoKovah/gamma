import React from 'react';
import { render } from '@testing-library/react';
import { toBeInTheDocument } from '@testing-library/jest-dom';
import FilterContainer from '../FilterContainer';

describe('FilterContainer', () => {
    global.fetch = jest.fn();
    let filtersChangedMock;
    let shouldFilterUpdateMock;
    const organisations = ['RG', 'TEST', 'EDX'];
    const courses = [
        'course-v1:RG+course-1+2022',
        'course-v1:EDX+course-2+2022',
        'course-v1:TEST+course-3+2023',
    ];

    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
        filtersChangedMock = jest.fn();
        shouldFilterUpdateMock = jest.fn();
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                json: () => Promise.resolve({ courses }),
            })
        );
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                json: () => Promise.resolve({ organisations }),
            })
        );
    });

    it('renders FilterContainer component', () => {
        const filters = { 
            org: 'RG',
            interval: {
                start: '10/10/2022',
                end: '12/12/2022'
            },
        };
        const { getByTestId } = render(
            <FilterContainer
                filters={filters}
                shouldFilterUpdate={shouldFilterUpdateMock}
                onChange={filtersChangedMock}
            />
        );

        expect(getByTestId('FilterItem')).toBeInTheDocument();
    });
});

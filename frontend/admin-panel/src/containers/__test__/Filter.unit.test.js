import React from 'react';
import { render, screen } from '@testing-library/react';
import { toBeInTheDocument } from '@testing-library/jest-dom';
import Filter from '../Filter';

describe('Filter component renders correctly with different props', () => {
    global.fetch = jest.fn();
    const organisations = ['RG', 'TEST', 'EDX'];
    const courses = [
        'course-v1:RG+course-1+2022',
        'course-v1:EDX+course-2+2022',
        'course-v1:TEST+course-3+2023',
    ];

    beforeEach(() => {
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
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('rendered with empty props', () => {
        const props = {};
        const { getByText } = render(<Filter {...props} />);

        expect(getByText('Filters')).toBeInTheDocument();
        expect(getByText('Add fields')).toBeInTheDocument();
        expect(screen.queryByText('Organisation')).not.toBeInTheDocument();
        expect(screen.queryByText('Courses')).not.toBeInTheDocument();
    });

    it('rendered with organisation props', () => {
        const props = {
            org: 'EDX',
        };
        const { getByText } = render(<Filter {...props} />);

        expect(getByText('Filters')).toBeInTheDocument();
        expect(getByText('Organisation')).toBeInTheDocument();
        expect(getByText('EDX')).toBeInTheDocument();
        expect(getByText('Add fields')).toBeInTheDocument();
        expect(screen.queryByText('Courses')).not.toBeInTheDocument();
    });

    it('rendered with course props', () => {
        const props = {
            course: 'course-v1:EDX+course-2+2022'
        };
        const { getByText } = render(<Filter {...props} />);

        expect(getByText('Filters')).toBeInTheDocument();
        expect(getByText('Courses')).toBeInTheDocument();
        expect(getByText('course-v1:EDX+course-2+2022')).toBeInTheDocument();
        expect(screen.queryByText('Organisation')).not.toBeInTheDocument();
    });

    it('rendered with both org and course props', () => {
        const props = {
            org: 'RG',
            course: 'course-v1:RG+course-1+2022'
        };
        const { getByText } = render(<Filter {...props} />);

        expect(getByText('Filters')).toBeInTheDocument();
        expect(getByText('Organisation')).toBeInTheDocument();
        expect(getByText('Courses')).toBeInTheDocument();
        expect(getByText('RG')).toBeInTheDocument();
        expect(getByText('course-v1:RG+course-1+2022')).toBeInTheDocument();
        expect(getByText('Add fields')).toBeInTheDocument();
    });
});

describe('tests for getCurrentOrganisations', () => {
    const emptySelectValue = [{ value: null, label: '-----' }];

    it('should return all organisations when no course is selected', () => {
        const organisations = ['Org1', 'Org2', 'Org3'];
        const result = Filter.prototype.getCurrentOrganisations(
            '',
            organisations,
            emptySelectValue
        );

        expect(result).toEqual([
            { value: null, label: '-----' },
            { value: 'Org1', label: 'Org1' },
            { value: 'Org2', label: 'Org2' },
            { value: 'Org3', label: 'Org3' }
        ]);
    });

    it('should return the organisation related to the selected course', () => {
        const organisations = ['Org1', 'Org2', 'Org3'];
        const result = Filter.prototype.getCurrentOrganisations(
            'course-v1:Org1+Demo_Course+2023',
            organisations,
            emptySelectValue
        );

        expect(result).toEqual([
            { value: null, label: '-----' },
            { value: 'Org1', label: 'Org1' }
        ]);
    });

    it('should return the course organization even if it is not in the list of organizations', () => {
        const organisations = ['Org1', 'Org2', 'Org3'];
        const result = Filter.prototype.getCurrentOrganisations(
            'course-v1:RG+Demo_Course+2023',
            organisations,
            emptySelectValue
        );

        expect(result).toEqual([
            { value: null, label: '-----' },
            { value: 'RG', label: 'RG' }
        ]);
    });
});

describe('tests for getCurrentCourses', () => {
    const emptySelectValue = [{ value: null, label: '-----' }];

    it('should return all courses when no organisation is selected', () => {
        const courses = [
            'course-v1:Org1+Demo_Course_1+2022',
            'course-v1:Org2+Demo_Course_2+2023',
            'course-v1:Org1+Demo_Course_3+2022',
            'course-v1:Org3+Demo_Course_4+2023'
        ];

        const result = Filter.prototype.getCurrentCourses(
            '',
            courses,
            emptySelectValue
        );
        expect(result).toEqual([
            {value: null, label: '-----' },
            {value: 'course-v1:Org1+Demo_Course_1+2022', label: 'course-v1:Org1+Demo_Course_1+2022'},
            {value: 'course-v1:Org2+Demo_Course_2+2023', label: 'course-v1:Org2+Demo_Course_2+2023'},
            {value: 'course-v1:Org1+Demo_Course_3+2022', label: 'course-v1:Org1+Demo_Course_3+2022'},
            {value: 'course-v1:Org3+Demo_Course_4+2023', label: 'course-v1:Org3+Demo_Course_4+2023'}
        ]);
    });

    it('should return courses related to the selected organisation', () => {
        const courses = [
            'course-v1:RG+Demo_Course_1+2022',
            'course-v1:Org+Demo_Course_2+2023',
            'course-v1:RG+Demo_Course_3+2022',
            'course-v1:Org+Demo_Course_4+2023'
        ];
        const result = Filter.prototype.getCurrentCourses(
            'RG',
            courses,
            emptySelectValue
        );

        expect(result).toEqual([
            {value: null, label: '-----' },
            {value: 'course-v1:RG+Demo_Course_1+2022', label: 'course-v1:RG+Demo_Course_1+2022'},
            {value: 'course-v1:RG+Demo_Course_3+2022', label: 'course-v1:RG+Demo_Course_3+2022'}
        ]);
    });

    it('should return none courses', () => {
        const courses = [
            'course-v1:Org2+Demo_Course_1+2022',
            'course-v1:Org2+Demo_Course_2+2023',
            'course-v1:Org3+Demo_Course_3+2022',
            'course-v1:Org4+Demo_Course_4+2023'
        ];
        const result = Filter.prototype.getCurrentCourses(
            'Org1',
            courses,
            emptySelectValue
        );

        expect(result).toEqual([
            {value: null, label: '-----' },
        ]);
    });

    it('should not return any courses, if list of courses is empty', () => {
        const courses = [];
        const result = Filter.prototype.getCurrentCourses(
            'Org',
            courses,
            emptySelectValue
        );

        expect(result).toEqual([
            {value: null, label: '-----' },
        ]);
    });
});

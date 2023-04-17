import React from 'react';
import { render } from '@testing-library/react';
import AndOrBlock from '../AndOrBlock';

describe('AndOrBlock component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('renders without crashing', () => {
        const div = document.createElement('div');
        render(<AndOrBlock />, div);
    });
});

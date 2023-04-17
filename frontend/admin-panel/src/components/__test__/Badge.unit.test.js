import React from 'react';
import { render } from '@testing-library/react';
import Badge from '../Badge';

describe('And component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        render(<Badge />, div);
    });
});

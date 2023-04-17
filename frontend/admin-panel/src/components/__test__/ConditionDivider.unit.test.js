import React from 'react';
import { render } from '@testing-library/react';
import ConditionDivider from '../ConditionDivider';

describe('ConditionDivider component', () => {
    it('renders without crashing', () => {
        const div = document.createElement('div');
        render(<ConditionDivider />, div);
    });
});

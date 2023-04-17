import React from 'react';
import {render} from '@testing-library/react';
import Or from '../Or';

describe('Or component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    afterEach(() => {
        delete window.gettext;
    });

    test('should render "or" button', () => {
        const {getByRole} = render(<Or onClick={() => {}} />);
        const orButton = getByRole('button', {name: 'or'});
        expect(orButton).toBeDefined();
    });
});

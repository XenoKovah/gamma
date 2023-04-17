import React from 'react';
import { render } from '@testing-library/react';
import { EventType, BadgeSelector, StatusBadgeSelector } from '../Select';

describe('Selector components', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });
    
    afterEach(() => {
        delete window.gettext;
    });

    it('should render EventType component without errors', () => {
        render(<EventType />);
    });

    it('should render BadgeSelector component without errors', () => {
        render(<BadgeSelector />);
    });

    it('should render StatusBadgeSelector component without errors', () => {
        render(<StatusBadgeSelector />);
    });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActionList from '../ActionList';

describe('ActionList component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it("renders without crashing", () => {
        render(<ActionList />);
        const actionListElements = screen.queryAllByText(/Actions/i);
        expect(actionListElements.length).toBe(2);
    });
});

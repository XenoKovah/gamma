import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import And from '../And';

describe('And component', () => {
    let mockOnClick;

    beforeEach(() => {
        mockOnClick = jest.fn();
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('should render "Add" button', () => {
        const { getByText } = render(<And onClick={mockOnClick} />);
        const addButton = getByText('Add');
        fireEvent.click(addButton);
        expect(mockOnClick).toHaveBeenCalled();
    });
});

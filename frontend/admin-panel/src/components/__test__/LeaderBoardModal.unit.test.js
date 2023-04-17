import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import LeaderBoardModal from '../LeaderBoardModal';

describe('LeaderBoardModal component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('renders without crashing', () => {
        const { getByTestId } = render(<LeaderBoardModal />);
        const leaderBoardModalElement = getByTestId('leaderboard-modal');
        expect(leaderBoardModalElement).toBeInTheDocument();
    });
});

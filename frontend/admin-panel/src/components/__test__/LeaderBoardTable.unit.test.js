import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import LeaderBoardTable from '../LeaderBoardTable';

describe('LeaderBoardTable component', () => {
    beforeEach(() => {
        window.gettext = jest.fn().mockImplementation((str) => str);
    });

    it('renders without crashing', () => {
        const gameProfiles = [
        {
            avatar: 'https://example.com/avatar.jpg',
            badges: ['https://example.com/badge1.jpg', 'https://example.com/badge2.jpg'],
            goal: 100,
            points: 50,
            position: 'student',
            user: { username: 'testUser' }
        }
        ];

        const { getByTestId } = render(<LeaderBoardTable gameProfiles={gameProfiles} />);
        const leaderBoardTableElement = getByTestId('leaderboard-table');
        expect(leaderBoardTableElement).toBeInTheDocument();
    });
});

import React from 'react';
import renderer from 'react-test-renderer';
import Badges from '../Badges';
import Badge from '../../components/Badge';

global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve([]),
    })
);

describe('Badges component', () => {
    it('should render the correct number of Badge components', async () => {
        const badgesComponent = renderer.create(<Badges />);
        await Promise.resolve();
        const children = badgesComponent.root.findAllByType(Badge);

        expect(children).toHaveLength(badgesComponent.getInstance().state.badges.length);
    });
});

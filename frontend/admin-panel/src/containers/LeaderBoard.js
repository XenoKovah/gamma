import React from 'react';

import LeaderboardModal from '../components/LeaderBoardModal';
import LeaderboardTable from '../components/LeaderBoardTable';

import {LEADERBOARD} from '../api/Api';

import '../styles/custom.scss';

export default class LeaderBoard extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            open: true,
            gameProfiles: [],
            rank: 0,
        }
    }

    componentDidMount() {
        fetch(process.env.REACT_APP_LOCALHOST + LEADERBOARD)
        .then(response => {
            return response.json()
        })
        .then((result) => {
            this.setState({
                gameProfiles: result.gameprofiles,
                rank: result.rank,
                badges: result.badges
            })
        })
    }

    render() {
        return (
            <LeaderboardModal history={this.props.history}>
                <LeaderboardTable gameProfiles={this.state.gameProfiles}/>
            </LeaderboardModal>
        )
    }
}
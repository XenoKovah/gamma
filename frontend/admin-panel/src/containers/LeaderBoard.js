import React from 'react';

import LeaderboardModal from '../components/LeaderBoardModal';
import LeaderboardTable from '../components/LeaderBoardTable';

import {LEADERBOARD} from '../api/Api';

import '../styles/custom.scss';

export default class LeaderBoard extends React.Component {

    constructor(props) {
        super(props);

        this.handleClose = this.handleClose.bind(this);

        this.state = {
            open: true,
            gameProfiles: [],
            rank: 0,
        }
    }

    handleClose() {
        this.props.history.push("/");
    }

    componentDidMount() {
        fetch(LEADERBOARD)
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
            <LeaderboardModal handleClose={this.handleClose}>
                <LeaderboardTable gameProfiles={this.state.gameProfiles}/>
            </LeaderboardModal>
        )
    }
}
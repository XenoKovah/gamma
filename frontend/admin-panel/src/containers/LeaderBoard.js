import React from 'react';

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
                <div className="LeaderboardModal">
                    <div className="LeaderboardModalWrapper">
                        <button className="LeaderboardModal-Close" onClick={this.handleClose}></button>
                        <div className="LeaderboardTable">
                            <div className="LeaderboardTableHead">
                                <div className="LeaderboardTableHead-Item">Students</div>
                                <div className="LeaderboardTableHead-Item">Progress</div>
                                <div className="LeaderboardTableHead-Item">Badges</div>
                            </div>
                            <div className="LeaderboardTableBody">
                                {
                                    this.state.gameProfiles.map((profile, ind) => {
                                        let progressClassName = `LeaderboardProgress-Status LeaderboardProgress-Status_${Math.floor(profile.points/10) * 10}`;
                                        let avatarUrl = `url(${profile.avatar})`;
                                        return (
                                            <div className="LeaderboardTableRow" key={ind}>
                                                <div className="LeaderboardTableWrapper LeaderboardPerson">
                                                    <figure className="LeaderboardPersonFigure" style={{'backgroundImage': avatarUrl}}>
                                                        <img src={profile.avatar} alt="avatar image" className="LeaderboardPerson-Photo"/>
                                                    </figure>
                                                    <div className="LeaderboardInfo">
                                                        <div className="LeaderboardPerson-Name">{profile.user.username}</div>
                                                        <div className="LeaderboardPerson-Profession">{profile.position}</div>
                                                    </div>
                                                </div>
                                                <div className="LeaderboardTableWrapper LeaderboardTableWrapper_center">
                                                    <div className="LeaderboardProgressWrapper">
                                                        <span className={progressClassName} style={{width: profile.points + '%'}}></span>
                                                    </div>
                                                </div>
                                                <div className="LeaderboardTableWrapper LeaderboardTableWrapper_center">
                                                    <div className="LeaderboardBadges">
                                                        {
                                                            profile.badges.map((badge, ind) => {
                                                                return (
                                                                    <span className="LeaderboardBadges-Icon" key={ind}>
                                                                        <img src={badge} alt="badge image" className="LeaderboardBadges-Icon"/>
                                                                    </span>
                                                                )
                                                            })
                                                        }
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })
                                }
                            </div>
                        </div>
                    </div>
                </div>
        )
    }
}
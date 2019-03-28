import React from 'react';


export default class LeaderBoardTable extends React.Component {

    render() {
        return this.props.gameProfiles.length > 0 ? (
            <div className="LeaderboardTable">
                <div className="LeaderboardTableHead">
                    <div className="LeaderboardTableHead-Item">Students</div>
                    <div className="LeaderboardTableHead-Item">Progress</div>
                    <div className="LeaderboardTableHead-Item">Badges</div>
                </div>
                <div className="LeaderboardTableBody">
                    {
                        this.props.gameProfiles.map((profile, ind) => {
                            let progressClassName = `LeaderboardProgress-Status LeaderboardProgress-Status_${Math.floor(profile.points/10) * 10}`;
                            let avatarUrl = `url(${profile.avatar})`;
                            return (
                                <div className="LeaderboardTableRow" key={ind}>
                                    <div className="LeaderboardTableWrapper LeaderboardPerson">
                                        <figure className="LeaderboardPersonFigure" style={{'backgroundImage': avatarUrl}}>
                                            <img src={process.env.REACT_APP_LOCALHOST + profile.avatar} alt="avatar image" className="LeaderboardPerson-Photo"/>
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
                                                            <img src={process.env.REACT_APP_LOCALHOST + badge} alt="badge image" className="LeaderboardBadges-Icon"/>
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
        ) : false
    }
}

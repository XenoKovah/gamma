import React from 'react';

import LeaderBoardModal from '../components/LeaderBoardModal';
import { BADGES } from '../api/Api';

export default class MoreBadges extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            badges: []
        }
    }

    componentDidMount() {
        let { username } = this.props.match.params;
        let { url } = this.props.match.params;
        let queryString = username ? `?username=${username}` : '';
        fetch(process.env.REACT_APP_LOCALHOST + BADGES + queryString)
        .then(res=>res.json())
        .then(result=> {
            this.setState({
                badges: result
            })
        })
    }

    render() {
        return this.state.badges ? (
            <LeaderBoardModal history={this.props.history} assistentClass={true} >
                {
                    Object.keys(this.state.badges).map((badge, ind) => {
                        let badgeItemClass = !this.state.badges[badge].done ? 
                            'BadgeItemFigure BadgeItemFigure_disable' : 'BadgeItemFigure';
                        return (
                            <div className="BadgeItem BadgeItem_center" key={ind}>
                                <div className={badgeItemClass}>
                                    <img src={process.env.REACT_APP_LOCALHOST + this.state.badges[badge].url} alt="" className="BadgeItemFigure-Image" />
                                </div>
                                <div className="BadgeItem-Name">{badge}</div>
                            </div>
                        )
                    })
                }
            </LeaderBoardModal>
        ) : false
    }
}

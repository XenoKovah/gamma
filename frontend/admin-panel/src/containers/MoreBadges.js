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
                        let imageSrc = this.state.badges[badge].url.startsWith('http')
                          ? this.state.badges[badge].url
                          : process.env.REACT_APP_LOCALHOST + this.state.badges[badge].url;

                        if(!this.state.badges[badge].done){
                        return (
                            <div className="BadgeItem BadgeItem_center" key={`${ind}-undone-badge-item`}>
                                <div className={badgeItemClass}>
                                    <img src={imageSrc} alt="" className="BadgeItemFigure-Image" />
                                </div>
                                <div className="BadgeItem-Name">{badge}</div>
                                <div className="BadgeItemPopup">
                                    <div className="BadgeItemPopup-Head">{badge}</div>
                                    <div className="BadgeItemPopup-Body">
                                    <ul className="BadgeItemPopupList">
                                        {
                                            Object.keys(this.state.badges[badge]['progress']).map((p, i)=>{
                                                return (
                                                    <li key={`${i}-badge-item-image`} className="BadgeItemPopupList-Item">
                                                        <span className="BadgeItemPopupList-Counter">
                                                            {this.state.badges[badge]['progress'][p]['count']} /  { this.state.badges[badge]['progress'][p]['goal']} {p[0].toUpperCase() + p.slice(1).toLowerCase()}
                                                        </span>
                                                    </li>
                                                )
                                            })
                                        }
                                    </ul>
                                    </div>
                                </div>
                            </div>
                        )
                        } else {
                            return (
                                <div className="BadgeItem BadgeItem_center" key={`${ind}-done-badge-item`}>
                                    <div className={badgeItemClass}>
                                        <img src={imageSrc} alt="" className="BadgeItemFigure-Image" />
                                    </div>
                                    <div className="BadgeItem-Name">{badge}</div>

                                </div>
                            )
                        }
                    })
                }
            </LeaderBoardModal>
        ) : false
    }
}

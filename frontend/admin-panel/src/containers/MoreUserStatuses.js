import React from 'react';

import LeaderBoardModal from '../components/LeaderBoardModal';
import { USER_STATUSES } from '../api/Api';

export default class MoreBadges extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            userStatuses: []
        }
    }

    componentDidMount() {
        let { username } = this.props.match.params;
        let { url } = this.props.match.params;
        let queryString = username ? `?username=${username}` : '';
        fetch(process.env.REACT_APP_LOCALHOST + USER_STATUSES + queryString)
        .then(res=>res.json())
        .then(result=> {
            this.setState({
                userStatuses: result
            })
        })
    }

    render() {
        return this.state.userStatuses ? (
            <LeaderBoardModal history={this.props.history} assistentClass={true}>
                {
                    this.state.userStatuses.map((status, ind) => {
                        let imageSrc = status.url.startsWith('http') ? status.url : process.env.REACT_APP_LOCALHOST + status.url;

                        if(status.status_points / status.progress <= 1){
                            return (
                                <div className="BadgeItem BadgeItem_center" key={ind}>
                                    <div className="BadgeItemFigure">
                                        <img src={imageSrc} alt="" className="BadgeItemFigure-Image" />
                                    </div>
                                    <div className="BadgeItem-Name">{status.title}</div>
                                </div>
                            )
                        } else {
                            return (
                                <div className="BadgeItem BadgeItem_center" key={ind}>
                                    <div className="BadgeItemFigure BadgeItemFigure_disable">
                                        <img src={imageSrc} alt="" className="BadgeItemFigure-Image" />
                                    </div>
                                    <div className="BadgeItem-Name">{status.title}</div>
                                    <div className="BadgeItemPopup">
                                        <div className="BadgeItemPopup-Head"></div>
                                        <div className="BadgeItemPopup-Body">
                                            <ul className="BadgeItemPopupList">
                                                <li className="BadgeItemPopupList-Item">
                                                    <span className="BadgeItemPopupList-Counter">
                                                    {status.progress}/{status.status_points}
                                                    </span>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            )
                        }
                    })
                }
            </LeaderBoardModal>
        ) : false
    }
}

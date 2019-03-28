import React from 'react';

export default class LeaderBoardModal extends React.Component {

    render() {
        return (
            <div className="LeaderboardModal">
                <div className="LeaderboardModalWrapper">
                    <button className="LeaderboardModal-Close" onClick={this.props.handleClose}></button>
                    {this.props.children}
                </div>
            </div>
        )
    }
}

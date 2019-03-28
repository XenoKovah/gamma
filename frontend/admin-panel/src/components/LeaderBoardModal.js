import React from 'react';

export default class LeaderBoardModal extends React.Component {

    handleClose() {
        this.props.history.push("/");
    }

    render() {
        return (
            <div className="LeaderboardModal">
                <div className="LeaderboardModalWrapper">
                    <button className="LeaderboardModal-Close" onClick={this.handleClose.bind(this)}></button>
                    {this.props.children}
                </div>
            </div>
        )
    }
}

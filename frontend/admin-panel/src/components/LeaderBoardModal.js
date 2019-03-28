import React from 'react';

export default class LeaderBoardModal extends React.Component {

    handleClose() {
        this.props.history.push("/");
    }

    render() {
      let wrapperClass = this.props.assistentClass ? 'LeaderboardModalWrapper LeaderboardModalWrapper_collection' : 'LeaderboardModalWrapper';
        return (
            <div className="LeaderboardModal">
                <div className={wrapperClass}>
                    <button className="LeaderboardModal-Close" onClick={this.handleClose.bind(this)}></button>
                    {this.props.children}
                </div>
            </div>
        )
    }
}

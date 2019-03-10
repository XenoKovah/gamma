import React, {Component} from 'react';

class And extends Component {
    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick(event) {
        this.props.onClick(event);
    }

    render() {
        return (
            <div className="AndButton AndOrButtonItem">
                <input type="button" value="and" onClick={this.handleClick}/>
            </div>
        )
    }
}

export default And;

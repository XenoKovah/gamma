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
            <button onClick={this.handleClick} className="Btn Btn_primary Btn_add">Add</button>
        )
    }
}

export default And;

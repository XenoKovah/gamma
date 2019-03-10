import React, {Component} from 'react';

class Or extends Component {

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick(event) {
        this.props.onClick(event);
    }

    render() {
        return (
            <div className="OrButton AndOrButtonItem">
                <input type="button" value="or" onClick={this.handleClick}/>
            </div>
        )
    }
}

export default Or;

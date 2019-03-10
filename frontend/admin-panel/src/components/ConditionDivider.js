import React, {Component} from 'react';

class ConditionDivider extends Component {

    constructor(props) {
        super(props);

    }

    render() {
        return this.props.value ? (
            <div className="ConditionDivider">
                <input type="button" disabled value={this.props.value}/>
            </div>
        ) : false
    }
}

export default ConditionDivider;

import React, {Component} from 'react';

import And from '../components/And';
import Or from '../components/Or';

class AndOrBlock extends Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="AndOrBlock">
                <And onClick={this.props.addCondition}/>
                {/* <Or onClick={this.props.addCondition}/> */}
            </div>
        )
    }
}

export default AndOrBlock;

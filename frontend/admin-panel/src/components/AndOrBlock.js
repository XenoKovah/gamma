import React, {Component} from 'react';

import And from '../components/And';

class AndOrBlock extends Component {

    render() {
        return (
            <And onClick={this.props.addCondition}/>
        )
    }
}

export default AndOrBlock;

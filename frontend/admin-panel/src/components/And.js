import React, {Component} from 'react';
import Button from '@material-ui/core/Button';

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
            <Button onClick={this.handleClick} size="small" fullWidth={true} className="AndOrButtonItem">Add</Button>
        )
    }
}

export default And;

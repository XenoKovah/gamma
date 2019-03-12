import React from 'react';

export default class Badge extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <img src={this.props.url} />
        )
    }
}

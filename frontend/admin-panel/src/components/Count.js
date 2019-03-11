import React from 'react';

class Count extends React.Component {

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
    }

    onChange(event) {
        this.setState({
            count: event.currentTarget.value
        }, () => {this.props.onChange(this.state)})
    }


    render() {
        return (
            <label>Enter count
                <input name="count" onChange={this.onChange} type="number"/>
            </label>
        )
    }
}

export default Count;

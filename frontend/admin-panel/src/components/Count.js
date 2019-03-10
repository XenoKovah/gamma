import React from 'react';

class Count extends React.Component {

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
    }

    onChange(event) {
        this.props.onChange({count: event.currentTarget.value});
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

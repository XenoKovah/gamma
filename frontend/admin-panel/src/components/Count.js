import React from 'react';

class Count extends React.Component {

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
        this.state = {
            count: this.props.count || ""
        }
    }

    onChange(event) {
        this.setState({
            count: event.currentTarget.value
        }, () => {this.props.onChanged(this.state)})
    }


    render() {
        return (
            <label>Enter count
                <input onChange={this.onChange} type="number" value={this.state.count}/>
            </label>
        )
    }
}

export default Count;

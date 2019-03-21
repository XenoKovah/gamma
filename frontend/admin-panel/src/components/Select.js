import React from 'react';
import Select from 'react-select';

class EventType extends React.Component {
    constructor(props) {
        super(props);
        
        this.handleChange = this.handleChange.bind(this);

        this.state = {
            action: this.props.action
        }
    }

    handleChange(event) {
        this.setState({
            action: event
        }, () => {this.props.onChanged(this.state)} )
    }

    render() {
        const options = this.props.actions.map((el, ind) => {
            return {value:el, label:el}
        });

        return (
            <div className="FormGroup">
                <label>Event type</label>
                <Select value={this.state.action} onChange={this.handleChange} className="Select" placeholder="-----"
                    value={this.state.action}
                    options={options}
                />
            </div>
        )
    }
}

export default EventType;

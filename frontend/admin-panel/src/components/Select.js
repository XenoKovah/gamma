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
            action: event.value
        }, () => {this.props.onChanged(this.state)} )
    }

    render() {
        let options = [{value: this.state.action, label: this.state.action}];

        const customStyles = {
            menu: (provided, state) => ({
                ...provided,
                width: 400,
            }),}
        this.props.actions.forEach((el, ind) => {
            options.push({value:el, label:el});
        });
        let defaultValue = {value:this.state.action, label:this.state.action};
        return (
            <div className="FormGroup">
                <label>Event type</label>
                <Select onChange={this.handleChange} className="Select event-type-select" placeholder="-----"
                    value={defaultValue}
                    options={options}
                    styles={customStyles}
                />
            </div>
        )
    }
}

export default EventType;

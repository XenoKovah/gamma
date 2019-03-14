import React from 'react';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormGroup from '@material-ui/core/FormGroup';

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
            action: event.currentTarget.value
        }, () => {this.props.onChanged(this.state)} )
    }

    render() {
        return (
            <FormGroup>
                <InputLabel htmlFor="problem-select">Event</InputLabel>
                <Select id="problem-select" native value={this.state.action} onChange={this.handleChange}>
                    <option key={0} value="">-----</option>
                    {
                        this.props.actions.map((el, ind) => {
                            return <option key={ind+1} value={el}>{el}</option>
                        })
                    }
                </Select>

            </FormGroup>
        )
    }
}

export default EventType;

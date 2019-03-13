import React from 'react';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormGroup from '@material-ui/core/FormGroup';

class EventType extends React.Component {
    constructor(props) {
        super(props);

        this.items = this.props.actions || ['one', 'two'];
        
        this.handleChange = this.handleChange.bind(this);
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
                <Select id="problem-select" native defaultValue={this.props.action} onChange={this.handleChange}>
                    <option key={0} value="-----">-----</option>
                    {
                        this.items.map((el, ind) => {
                            return <option key={ind+1} value={el}>{el}</option>
                        })
                    }
                </Select>

            </FormGroup>
        )
    }
}

export default EventType;

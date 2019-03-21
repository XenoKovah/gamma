import React from 'react';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';

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
            <FormControl>
                <label >Event</label>
                <select value={this.state.action} onChange={this.handleChange} autoWidth={true} className="Select">
                    <option key={0} value={this.state.action}>{this.state.action}</option>
                    {
                        this.props.actions.map((el, ind) => {
                            return <option key={ind+1} value={el}>{el}</option>
                        })
                    }
                </select>

            </FormControl>
        )
    }
}

export default EventType;

import React from 'react';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';

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
            <FormControl>
                <InputLabel htmlFor="count-input">Count </InputLabel>
                <Input id="count-input"
                defaultValue={this.state.count} 
                onChange={this.onChange} />

            </FormControl>
            
        )
    }
}

export default Count;

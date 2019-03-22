import React from 'react';
import InputNumber from 'rc-input-number';

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
            count: event
        }, () => {this.props.onChanged(this.state)})
    }


    render() {
        return (
            <div className="FormGroup">
                <label htmlFor="count-input">Count</label>
                <InputNumber id="count-input" inputProps={{type: "number"}} min={1}
                    defaultValue={this.state.count} 
                    onChange={this.onChange} />

            </div>
            
        )
    }
}

export default Count;

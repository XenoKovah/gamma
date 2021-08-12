import React from 'react';
import InputNumber from 'rc-input-number';

class Count extends React.Component {

    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
    }

    onChange(event) {
        this.props.onChanged({count: event});
    }

    render() {
        return (
            <div className="FormGroup">
                <label htmlFor="count-input">{gettext('Count')}</label>
                <InputNumber id="count-input" inputProps={{type: "number"}} min={1}
                    value={this.props.count}
                    onChange={this.onChange} />
            </div>
        )
    }
}

export default Count;

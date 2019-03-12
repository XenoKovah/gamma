import React from 'react';

class Select extends React.Component {
    constructor(props) {
        super(props);
        this.items = ['one', 'two', 'three', 'four'];
        
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        this.setState({
            action: event.currentTarget.value
        }, () => {this.props.onChanged(this.state)} )
    }

    render() {
        let options = this.items.map((el, ind) => {
            let defaultValue = el === this.props.action;
            return <option key={ind} value={el} selected={defaultValue}>{el}</option>
        });
        return (
            <label>Choose action
                <select onChange={this.handleChange}>
                    <option value="----">-----</option>
                    {options}
                </select>
            </label>
        )
    }
}

export default Select;

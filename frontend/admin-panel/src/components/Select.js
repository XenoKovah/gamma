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
        }, () => {this.props.onChange(this.state)} )
    }

    render() {
        let options = this.items.map((el, ind) => {
            return <option key={ind} value={el}>{el}</option>
        });
        return (
            <label>Choose action
                <select onChange={this.handleChange}>
                    <option value="----" defaultValue>-----</option>
                    {options}
                </select>
            </label>
        )
    }
}

export default Select;

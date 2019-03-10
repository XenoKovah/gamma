import React from 'react';

class Select extends React.Component {
    constructor(props) {
        super(props);
        this.items = props.items ? props.items : ['one', 'two', 'three', 'four'];
        
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        this.props.onChange({action: event.currentTarget.value});
    }

    render() {
        let options = this.items.map((el, ind) => {
            return <option key={ind} value={el}>{el}</option>
        });
        return (
            <label>Choose action
                <select onChange={this.handleChange}>
                    <option value="----" selected>-----</option>
                    {options}
                </select>
            </label>
        )
    }
}

export default Select;

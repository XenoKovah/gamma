import React from 'react';

import Select from './Select';
import Count from './Count';
import ConditionDivider from './ConditionDivider';


class FilterContainer extends React.Component {

    constructor(props) {
        super(props);

        this.selectChanged = this.selectChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);

        this.state = {
            action: "",
            count:0
        }
    }

    selectChanged(data) {
        this.setState({
            ...data
        }, () => {
            this.props.onChange(this.props.id, this.state, this.props.value);
        })
        
    }

    deleteBlock(event) {
        event.preventDefault();
        this.props.deleteBlock(this.props.id);
    }

    render() {
        return (
            <div className="BlockFilter" data-id={this.props.id}>
                <ConditionDivider value={this.props.value}/>
                <div className="BlockFilter-item">
                    <Select onChange={this.selectChanged}/>
                </div>
                <div className="BlockFilter-item">
                    <Count onChange={this.selectChanged}/>
                </div>
                {
                    this.props.value ? <button onClick={this.deleteBlock}>Delete</button> : false
                }
            </div>
        )
    }
}

export default FilterContainer;

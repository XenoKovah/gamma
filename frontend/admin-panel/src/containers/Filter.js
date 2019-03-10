import React from 'react';
import Dropdown from 'react-dropdown';

import FilterContainer from '../components/FilterContainer';
import AndOrBlock from '../components/AndOrBlock';

import '../styles/custom.css'

const options = [
    'one',
    'two',
    'three'
]

class Filter extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.addCondition = this.addCondition.bind(this);
        this.orCondition = this.orCondition.bind(this);
        this.selectChanged = this.selectChanged.bind(this);

        this.defaultOption = options[0];
        this.state = {
            conditions: [{value: undefined}],
            filters: []
        }

        this.conditionMapping = {
            and: '&&',
            or: '||'
        };

    }

    selectChanged(id, state, conditionValue) {
        let filters = this.state.filters;
        filters[id] = {condition: conditionValue, ...state};
        this.setState({
            filters: filters
        });
    }

    get() {
        fetch('/api/v0/points?username=staff')
        .then(res => res.json())
        .then(result => {
            console.log(result);
        },
        error => {
            console.log(error);
        })
    }

    handleSubmit(event) {
        event.preventDefault();
        if (this.state.filters.length) {
            console.log(this.state.filters);
        } else {
            alert('You havent choosen anything!');
        }
    }

    addCondition(event) {
        let key = this.state.conditions.length + 1;
        let value = this.conditionMapping[event.currentTarget.value];
        this.setState({
            conditions: this.state.conditions.concat([{value: value}])
        });

    }

    orCondition(event) {
        console.log('OR condition clicked');
    }

    render() {
        return (
            <div className="Filter">
                <form onSubmit={this.handleSubmit}>
                    <h3>Filter!</h3>
                    {
                        this.state.conditions.map((el, ind) => {
                            return <FilterContainer key={ind} id={ind} onChange={this.selectChanged} {...el} />
                        })
                    }
                    <AndOrBlock addCondition={this.addCondition}/>
                    <input type="submit" value="Submit" className="FormSubmit" />
                </form>
            </div>
        )
    }

}

export default Filter;

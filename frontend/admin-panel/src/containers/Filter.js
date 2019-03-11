import React from 'react';

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
        this.selectChanged = this.selectChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);

        this.defaultOption = options[0];
        this.state = {
            conditions: [{value: undefined}],
            filters: []
        }

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
            let validFilters = this.state.filters.filter((filter, ind) => {
                return filter.count && filter.action
            })
            console.log(validFilters);
        } else {
            alert('You havent choosen anything!');
        }
    }

    addCondition(event) {
        this.setState({
            conditions: this.state.conditions.concat([{value: event.currentTarget.value}])
        }, () => {console.log(this.state.conditions)});

    }

    deleteBlock(id) {
        const conditions = this.state.conditions.filter((el, ind) => {
            console.log(ind, id);
            return ind !== id;
        });
        console.log(conditions, this.state.conditions);
        this.setState({
            conditions: conditions
        })
    }

    render() {
        return (
            <div className="Filter">
                <form onSubmit={this.handleSubmit}>
                    <h3>Filter!</h3>
                    {
                        this.state.conditions.map((el, ind) => {
                            return <FilterContainer key={ind} id={ind} onChange={this.selectChanged} deleteBlock={this.deleteBlock} {...el} />
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

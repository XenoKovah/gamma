import React from 'react';

import ActionContainer from '../components/ActionContainer';
import AndOrBlock from '../components/AndOrBlock';

import '../styles/custom.css';

class Action extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.addCondition = this.addCondition.bind(this);
        this.containerChanged = this.containerChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.getConditions = this.getConditions.bind(this);

        this.state = {
            conditions: [{condition: "", action: "", count: 0, id: 0}]
        }

    }

    getConditions() {
        return []
    }

    containerChanged(id, key, value) {
        console.log(id, key, value);
        let newConditions = Object.assign([], this.state.conditions);

        newConditions[id][key] = value;
        this.setState({
            conditions: newConditions
        })
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
        if (this.state.conditions.length) {
            let validConditions = this.state.conditions.filter((condition, ind) => {
                return condition.count && condition.action
            })
            console.log(validConditions);
        } else {
            alert('You havent choosen anything!');
        }
    }

    addCondition(event) {
        const newConditions = Object.assign([], this.state.conditions);
        let id = this.state.conditions.length;
        newConditions.push({condition: event.currentTarget.value, action: "", count: 0, id: id});
        this.setState({
            conditions: newConditions
        });

    }

    deleteBlock(id) {
        const newCond = Object.assign([], this.state.conditions);
        newCond.splice(id, 1);
        this.setState({
            conditions: newCond
        })
    }

    render() {
        const conditions = Object.assign([], this.state.conditions);
        return (
            <div className="Action">
                <form onSubmit={this.handleSubmit}>
                    <h3>Action</h3>
                    {
                        conditions.map((el, ind) => {
                            return (
                                <ActionContainer 
                                    key={el.id}
                                    id={ind} 
                                    onChange={this.containerChanged} 
                                    deleteBlock={this.deleteBlock}
                                    action={el.action}
                                    condition={el.condition}
                                    count={el.count}  
                                />
                            )
                        })
                    }
                    <AndOrBlock addCondition={this.addCondition}/>
                    <input type="submit" value="Submit" className="FormSubmit" />
                </form>
            </div>
        )
    }

}

export default Action;

import React from 'react';
import Button from '@material-ui/core/Button';

import ActionContainer from '../components/ActionContainer';
import AndOrBlock from '../components/AndOrBlock';

import '../styles/custom.css';

class Actions extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.addCondition = this.addCondition.bind(this);
        this.containerChanged = this.containerChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.getConditions = this.getConditions.bind(this);

        this.state = {
            conditions: [{action: "", count: 0, id: Math.random()}]
        }

    }

    getConditions() {
        return []
    }

    getConditionIndex(conditions, id) {
        let index;
        conditions.map((el, ind) => {
            if (el.id === id) {
                index = ind;
            }
        });
        return index;
    }

    containerChanged(id, key, value) {
        console.log('ID - ', id);
        let conditions = Object.assign([], this.state.conditions);
        console.log(conditions[this.getConditionIndex(conditions, id)]);
        conditions[this.getConditionIndex(conditions, id)][key] = value;
        this.setState({
            conditions: conditions
        })
    }

    get() {
        fetch('http://localhost:9000/api/v0/events/')
        .then(res => res.json())
        .then(result => {
            let actions = [];
            let data = result.map(el => {
                actions.push(el.event_type);
                return {action: el.event_type, count: el.award, id: el.id};
            });
            this.setState({
                conditions: data,
                actions: actions
            })
        },
        error => {
            console.log(error);
        })
    }

    componentDidMount() {
        this.get();
    }

    handleSubmit(event) {
        event.preventDefault();
        if (this.state.conditions.length) {
            let validConditions = this.state.conditions.filter((condition, ind) => {
                return condition.count && condition.action
            })
            const data = validConditions.map((el) => {
                let item = {};
                item[el.action] = el.count;
                return item;
            });
            console.log(data);
        } else {
            alert('You havent choosen anything!');
        }
    }

    addCondition(event) {
        const newConditions = Object.assign([], this.state.conditions);
        newConditions.push({action: "", count: 0, id: Math.random(), condition: "and"});
        this.setState({
            conditions: newConditions
        });

    }

    deleteBlock(id) {
        const { conditions } = this.state;
        conditions.splice(this.getConditionIndex(conditions, id), 1);
        this.setState({
            conditions: conditions
        })
    }

    render() {
        return (

                <form>
                    <h3>Actions</h3>
                    {
                        this.state.conditions.map((el, ind) => {
                            console.log('MAP, el = ', el);
                            return (
                                <ActionContainer 
                                    key={el.id}
                                    id={el.id} 
                                    onChange={this.containerChanged} 
                                    deleteBlock={this.deleteBlock}
                                    action={el.action}
                                    count={el.count}  
                                    actions={this.state.actions}
                                    condition={el.condition}
                                />
                            )
                        })
                    }
                    <AndOrBlock addCondition={this.addCondition}/>
                    <hr/>
                    <Button onClick={this.handleSubmit} size="large" color="primary">Save</Button>
                    <Button size="large" color="primary">Delete</Button>
                </form>

        )
    }

}

export default Actions;

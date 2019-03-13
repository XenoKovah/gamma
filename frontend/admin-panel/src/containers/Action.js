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
            actions: [],
            filters: [],
            eventTypes: []
        }
    }

    getConditions() {
        return []
    }

    getIndex(conditions, id) {
        let index;
        conditions.map((el, ind) => {
            if (el.id === id) {
                index = ind;
            }
        });
        return index;
    }

    containerChanged(id, key, value) {
        let actions = this.state.actions;
        let actionToChange = this.getIndex(actions, id);
        actions[actionToChange][key] = value;
        this.setState({
            actions: actions
        })
    }

    getRules() {
        fetch('http://localhost:9000/api/v0/badge-rules/?slug=performance')
        .then(res => res.json())
        .then(result => {
            let actions = [];
            let eventTypes = [];

            for (let key in result.actions) {
                actions.push(
                    {
                        id: Math.random(),
                        action: key,
                        count: result.actions[key]
                    }
                )
            }
            for (let key in result.event_types) {
                eventTypes.push(result.event_types[key]["event_type"])
            }
            this.setState({
                actions: actions,
                filters: result.filters,
                eventTypes: eventTypes
            })
        },
        error => {
            console.log(error);
        })
    }

    componentWillMount() {
        this.getRules();
    }

    handleSubmit(event) {
        event.preventDefault();
        if (this.state.actions.length) {
            let validActions = this.state.actions.filter((action, ind) => {
                return action.count && action.action
            })
            const data = validActions.map((el) => {
                let item = {};
                item[el.action] = +el.count;
                return item;
            });
            console.log(data);
        } else {
            alert('You havent choosen anything!');
        }
    }

    addCondition(event) {
        const actions = Object.assign([], this.state.actions);
        actions.push({action: "", count: 0, id: Math.random()});
        this.setState({
            actions: actions
        });

    }

    deleteBlock(id) {
        const { actions } = this.state;
        actions.splice(this.getIndex(actions, id), 1);
        this.setState({
            actions: actions
        })
    }

    render() {
        return (
                <form>
                    <h3>Actions</h3>
                    {
                        this.state.actions.map(el => {
                            return <ActionContainer 
                                key={el.id}
                                id={el.id} 
                                onChange={this.containerChanged} 
                                deleteBlock={this.deleteBlock}
                                action={el.action}
                                count={el.count}  
                                actions={this.state.eventTypes}
                            />
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

import React from 'react';
import Button from '@material-ui/core/Button';

import PropTypes from 'prop-types';

import ActionContainer from '../components/ActionContainer';
import AndOrBlock from '../components/AndOrBlock';

import '../styles/custom.css';

export default class Actions extends React.Component {
    constructor(props) {
        super(props);
        // this.handleSubmit = this.handleSubmit.bind(this);
        this.addCondition = this.addCondition.bind(this);
        this.containerChanged = this.containerChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.getConditions = this.getConditions.bind(this);

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
        let actions = this.props.actions;
        let actionToChange = this.getIndex(actions, id);
        actions[actionToChange][key] = value;
        this.props.onChangeProps('actions', actions);
    }

    addCondition(event) {
        const actions = Object.assign([], this.props.actions);
        actions.push({action: "", count: 0, id: Math.random()});
        this.props.onChangeProps('actions', actions);

    }

    deleteBlock(id) {
        const { actions } = this.props;
        actions.splice(this.getIndex(actions, id), 1);
        this.props.onChangeProps('actions', actions);
    }

    render() {
        return (
                <div>
                    <h3>Actions</h3>
                    {
                        this.props.actions.map(el => {
                            return <ActionContainer 
                                key={el.id}
                                id={el.id} 
                                onChange={this.containerChanged} 
                                deleteBlock={this.deleteBlock}
                                action={el.action}
                                count={el.count}  
                                actions={this.props.eventTypes}
                            />
                        })
                    }
                    <AndOrBlock addCondition={this.addCondition}/>
                </div>

        )
    }

}

Actions.propTypes = {
    actions: PropTypes.array,
    filters: PropTypes.object,
    eventTypes: PropTypes.array,
    onChangeProps: PropTypes.func,
    putRules: PropTypes.func,
}

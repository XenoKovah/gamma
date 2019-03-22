import React from 'react';

import ActionContainer from '../containers/ActionContainer';
import AndOrBlock from '../components/AndOrBlock';

import '../styles/custom.scss';

export default class Actions extends React.Component {
    constructor(props) {
        super(props);
        this.addCondition = this.addCondition.bind(this);
        this.containerChanged = this.containerChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.getActions = this.getActions.bind(this);
        this.updateAvailableActions = this.updateAvailableActions.bind(this);

        this.state = {
            allActions: [],
            availableActions: []
        }

    }

    getActions() {
        fetch('http://localhost:9000/api/v0/actions/')
        .then(resp => resp.json())
        .then(result => {
            let actions = result.map((el) => {
                return el.event_type;
            })
            this.updateAvailableActions(actions);
        })
    }

    updateAvailableActions(actions) {
        let actionList = actions || this.state.allActions;
        let occupiedActions = [];
        this.props.actions.forEach((action) => {
            if (actionList.indexOf(action.action) > -1) {
                occupiedActions.push(action.action)
            }
        });
        let available = actionList.filter((el) => {
            return occupiedActions.indexOf(el) === -1;
        })

        this.setState({
            allActions: actionList,
            availableActions: available
        })
    }

    componentDidMount() {
        this.getActions();
    }

    containerChanged(id, key, value) {
        let actions = this.props.actions;
        let actionToChange = this.props.getIndex(actions, id);
        actions[actionToChange][key] = value;
        this.updateAvailableActions();
        this.setState({
            actions: actions
        })

        this.props.onChangeProps('actions', actions);
    }

    addCondition(event) {
        const actions = Object.assign([], this.props.actions);
        actions.push({action: "", count: 0, id: Math.random()});
        this.props.onChangeProps('actions', actions);

    }

    deleteBlock(id) {
        const { actions } = this.props;
        actions.splice(this.props.getIndex(actions, id), 1);
        this.updateAvailableActions();
        this.props.onChangeProps('actions', actions);
    }

    render() {
        return (
                <div>
                    <h3>Actions</h3>
                    <div>
                        {
                            this.props.actions.map(el => {
                                return <ActionContainer
                                    key={el.id}
                                    id={el.id}
                                    onChange={this.containerChanged}
                                    deleteBlock={this.deleteBlock}
                                    action={el.action}
                                    count={el.count}
                                    actions={this.props.actions}
                                    availableActions={this.state.availableActions}
                                />
                            })
                        }
                        {
                            this.state.availableActions.length ? (<div>
                                <AndOrBlock addCondition={this.addCondition}/>
                            </div>) : false
                        }
                    </div>
                </div>

        )
    }

}

// Actions.propTypes = {
//     actions: PropTypes.array,
//     filters: PropTypes.array,
//     eventTypes: PropTypes.array,
//     onChangeProps: PropTypes.func,
//     putRules: PropTypes.func,
// }

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
        this.updateAvailableItems = this.updateAvailableItems.bind(this);
        this.getBadges = this.getBadges.bind(this);
        this.getStatusBadges = this.getStatusBadges.bind(this);

        this.allActions = [];
        this.allBadges = [];
        this.allStatusBadges = [];

        this.state = {
            availableActions: [],
            availableBadges: []
        }

    }

    getActions() {
        fetch('/api/v0/actions/')
        .then(resp => resp.json())
        .then(result => {
            let actions = result.map((el) => {
                return el.event_type;
            })
            this.allActions = actions;
            this.updateAvailableItems();
        })
    }

    getBadges() {
        fetch('/api/v0/badges-list/')
        .then(resp => resp.json())
        .then(result => {
            this.allBadges = result;
            this.updateAvailableItems();
        })
    }

    getStatusBadges() {
        fetch('/api/v0/status-badges-list/')
        .then(resp => resp.json())
        .then(result => {
            let statusBadges = result.map((el) => {
                return el.slug;
            })
            this.allStatusBadges = statusBadges;
            this.updateAvailableItems();
        })
    }

    updateAvailableItems() {
        // actions param is passed to function after initial actions api call  (on show of form popup),
        // the list from actions param is set to this.state.allActions,
        // at next calls value from this.state.allActions is used

        let availableBadges = [...this.allBadges];
        this.props.actions.forEach((action) => {
            if(action.action === 'badge'){
                let badgeIndex = availableBadges.indexOf(action.value);
                if(badgeIndex > -1){
                    availableBadges.splice(badgeIndex, 1);
                }
            }
        });

        let occupiedActions = [];
        this.props.actions.forEach((action) => {
            if (this.allActions.indexOf(action.action) > -1) {
                occupiedActions.push(action.action)
            }
        });
        let availableActions = this.allActions.filter((el) => {
            if (el === 'badge'){
                // 'badge' action should be visible only if there is available badges,
                // could be used more than once until available badges not finished
                return availableBadges.length > 0;
            }
            if (el === 'status_badge'){
                // 'status_badge' action should be visible only if there is available status badges,
                // could be used only once because status badges are sequential
                return occupiedActions.indexOf(el) === -1 && this.allStatusBadges.length > 0;
            }
            return occupiedActions.indexOf(el) === -1;
        });

        this.setState({
            availableBadges: availableBadges,
            availableActions: availableActions
        });
    }

    componentDidMount() {
        this.getBadges();
        this.getActions();
        this.getStatusBadges();
    }

    containerChanged(id, key, value) {
        let actions = this.props.actions;
        let actionToChange = this.props.getIndex(actions, id);

        const typesToClearValue = ["badge", "status_badge"];
        if(key === 'action' && (typesToClearValue.includes(value) ||
                                typesToClearValue.includes(actions[actionToChange].action))){
            actions[actionToChange]['value'] = null;
        }
        actions[actionToChange][key] = value;
        this.updateAvailableItems();

        this.props.onChangeProps('actions', actions);
    }

    addCondition(event) {
        const actions = Object.assign([], this.props.actions);
        actions.push({action: "", value: null, id: Math.random()});
        this.props.onChangeProps('actions', actions);

    }

    deleteBlock(id) {
        const { actions } = this.props;
        actions.splice(this.props.getIndex(actions, id), 1);
        this.updateAvailableItems();
        this.props.onChangeProps('actions', actions);
    }

    render() {
        return (
                <div>
                    <h3>{gettext('Actions')}</h3>
                    <div>
                        {
                            this.props.actions.map(el => {
                                return <ActionContainer
                                    key={el.id}
                                    id={el.id}
                                    onChange={this.containerChanged}
                                    deleteBlock={this.deleteBlock}
                                    action={el.action}
                                    value={el.value}
                                    actions={this.props.actions}
                                    availableActions={this.state.availableActions}

                                    availableBadges={this.state.availableBadges}
                                    statusBadges={this.allStatusBadges}
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

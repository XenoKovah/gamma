import React from 'react';

import { EventType, BadgeSelector, StatusBadgeSelector } from '../components/Select';
import Count from '../components/Count';


class ActionContainer extends React.Component {

    constructor(props) {
        super(props);
        this.actionChanged = this.actionChanged.bind(this);
        this.badgeChanged = this.badgeChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.countChanged = this.countChanged.bind(this);
        this.badgeChanged = this.badgeChanged.bind(this);

        this.state = {
            id: this.props.id || Math.random(),
            action: this.props.action || "",
            value: this.props.value || "",
            actions: this.props.actions || [],
            availableActions: this.props.availableActions || [],
            availableBadges: this.props.availableBadges || [],
        }
    }

    actionChanged(selectEvent) {
        this.setState({
            action: selectEvent.value
        }, () => {
            this.props.onChange(this.props.id, "action", selectEvent.value);
        });
    }

    badgeChanged(selectEvent) {
        this.setState({
            value: selectEvent.value
        }, () => {
            this.props.onChange(this.props.id, "value", selectEvent.value);
        });
    }

    countChanged(data) {
        this.setState({
            value: data.count
        }, () => {
            this.props.onChange(this.props.id, "value", data.count);
        });
    }

    deleteBlock(event) {
        event.preventDefault();
        this.props.deleteBlock(this.props.id);
    }

    render() {
        let valueComponent = null;

        switch(this.state.action){
            case 'badge':
                valueComponent = <BadgeSelector
                                 onChanged={this.badgeChanged}
                                 badge={this.props.value}
                                 badges={this.props.availableBadges}/>;
                break;
            case 'status_badge':
                valueComponent = <StatusBadgeSelector
                                 onChanged={this.badgeChanged}
                                 badge={this.props.value}
                                 badges={this.props.statusBadges}/>;
                break;
            default: // for various events and empty item
                valueComponent = <Count onChanged={this.countChanged} count={this.props.value}/>;
        }

        return (
            <div className="ActionItem">
                <EventType 
                    onChanged={this.actionChanged}
                    action={this.props.action}
                    actions={this.props.availableActions}/>
                {valueComponent}
                <button onClick={this.deleteBlock} className="Btn Btn_danger">{gettext('Delete')}</button>
            </div>
        )
    }
}

export default ActionContainer;

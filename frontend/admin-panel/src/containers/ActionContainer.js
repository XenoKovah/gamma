import React from 'react';

import EventType from '../components/Select';
import Count from '../components/Count';


class ActionContainer extends React.Component {

    constructor(props) {
        super(props);
        this.selectChanged = this.selectChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.countChanged = this.countChanged.bind(this);



        this.state = {
            id: this.props.id || Math.random(),
            action: this.props.action || "",
            count: this.props.count || "",
            actions: this.props.actions || [],
            availableActions: this.props.availableActions || []
        }
    }

    selectChanged(data) {
        this.setState({
            action: data.action
        }, () => {
            this.props.onChange(this.props.id, "action", data.action);
        }) 
    }

    countChanged(data) {
        this.setState({
            count: data.count
        }, () => {
            this.props.onChange(this.props.id, "count", data.count);
        })
    }

    deleteBlock(event) {
        event.preventDefault();
        this.props.deleteBlock(this.props.id);
    }

    render() {
        return (
            <div className="ActionItem">
                <EventType 
                    onChanged={this.selectChanged} 
                    action={this.props.action} 
                    actions={this.props.availableActions}/>
                <Count onChanged={this.countChanged} count={this.props.count}/>
                <button onClick={this.deleteBlock} className="Btn Btn-Danger">Delete</button>
            </div>
        )
    }
}

export default ActionContainer;

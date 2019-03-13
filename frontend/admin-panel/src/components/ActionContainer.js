import React from 'react';
import Button from '@material-ui/core/Button';

import EventType from './Select';
import Count from './Count';
import ConditionDivider from './ConditionDivider';


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
            actions: this.props.actions || []
        }
    }

    selectChanged(data) {
        console.log('ActionContainer, selectChanged - ', this.props.id);
        this.setState({
            action: data.action
        }, () => {
            this.props.onChange(this.props.id, "action", data.action);
        }) 
    }

    countChanged(data) {
        console.log('ActionContainer, countChanged - ', this.props.id);
        this.setState({
            count: data.count
        }, () => {
            this.props.onChange(this.props.id, "count", data.count);
        })
    }

    deleteBlock(event) {
        event.preventDefault();
        console.log(this.props.id);
        this.props.deleteBlock(this.props.id);
    }

    render() {
        console.log(this.props.actions, this.props.action)
        return (
            <div className="BlockAction">
                {/* <ConditionDivider value={this.props.condition}/> */}
                <EventType onChanged={this.selectChanged} action={this.props.action} actions={this.props.actions}/>
                <div className="BlockAction-item">
                    <Count onChanged={this.countChanged} count={this.props.count}/>
                </div>
                <Button onClick={this.deleteBlock}>Delete</Button>
            </div>
        )
    }
}

export default ActionContainer;

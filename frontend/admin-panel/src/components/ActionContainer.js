import React from 'react';

import Select from './Select';
import Count from './Count';
import ConditionDivider from './ConditionDivider';


class ActionContainer extends React.Component {

    constructor(props) {
        super(props);

        this.selectChanged = this.selectChanged.bind(this);
        this.deleteBlock = this.deleteBlock.bind(this);
        this.countChanged = this.countChanged.bind(this);


        console.log('ActionContainer constructor - props = ', this.props);
        this.state = {
            id: this.props.id || 0,
            action: this.props.action || "",
            count: this.props.count || "",
            condition: this.props.condition || ""
        }
    }

    selectChanged(data) {
        this.setState({
            action: data.action
        }, () => {
            this.props.onChange(this.props.id, "action", this.state.action);
        }) 
    }

    countChanged(data) {
        this.setState({
            count: data.count
        }, () => {
            this.props.onChange(this.props.id, "count", this.state.count);
        })
    }

    deleteBlock(event) {
        event.preventDefault();
        this.props.deleteBlock(this.props.id);
    }

    render() {
        return (
            <div className="BlockAction">
                <ConditionDivider value={this.props.condition}/>
                <div className="BlockAction-item">
                    <Select onChanged={this.selectChanged} action={this.props.action}/>
                </div>
                <div className="BlockAction-item">
                    <Count onChanged={this.countChanged} count={this.props.count}/>
                </div>
                {
                    this.props.condition ? <button onClick={this.deleteBlock}>Delete</button> : false
                }
            </div>
        )
    }
}

export default ActionContainer;

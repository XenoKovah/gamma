import React from 'react';
import Select from 'react-select';

class DropdownSelector extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        this.props.onChanged(event);
    }

    render() {

        const customStyles = {
            menu: (provided, state) => ({
                ...provided,
                width: 400,
            }),}

        return (
            <div className="FormGroup">
                <label>{this.props.label}</label>
                <Select onChange={this.handleChange} className="Select event-type-select" placeholder="-----"
                    value={this.props.value}
                    options={this.props.options}
                    styles={customStyles}
                />
            </div>
        )
    }
}

class EventType extends React.Component {

    render() {
        let options = [{value: this.props.action, label: this.props.action}];
        let actions = this.props.actions || [];
        for (const el of actions){
            // Special case for badge type because it's visibility at the list depends on non-used badges present
            // so 'badge' event type could be used more than once.
            // So if 'badge' is selected, don't push it to array if found, because it's already at first place
            if(this.props.action !== 'badge' || el !== 'badge'){
                options.push({value:el, label:el});
            }
        }
        let defaultValue = {value: this.props.action, label: this.props.action};

        return (
            <DropdownSelector
                label="Event type"
                value={defaultValue}
                options={options}
                onChanged={this.props.onChanged}
            />
        )
    }
}

class BadgeSelector extends React.Component {

    render() {
        let options = [{value: this.props.badge, label: this.props.badge}];
        let badges = this.props.badges || [];
        badges.forEach((el, ind) => {
            options.push({value:el, label:el});
        });
        let defaultValue = {value: this.props.badge, label: this.props.badge};

        return (
            <DropdownSelector
                label="Badge type"
                value={defaultValue}
                options={options}
                onChanged={this.props.onChanged}
            />
        )
    }
}


class StatusBadgeSelector extends React.Component {

    render() {
        let options = [{value: this.props.badge, label: this.props.badge}];
        let badges = this.props.badges || [];

        for (const el of badges){
            // Selected element should be set to the first place of the dropdown list
            if(this.props.badge !== el){
                options.push({value:el, label:el});
            }
        }

        let defaultValue = {value: this.props.badge, label: this.props.badge};

        return (
            <DropdownSelector
                label="Status Badge type"
                value={defaultValue}
                options={options}
                onChanged={this.props.onChanged}
            />
        )
    }
}


export { EventType, BadgeSelector, StatusBadgeSelector };

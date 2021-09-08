import React from 'react';
import Select from 'react-select';


export const customStyles = {
    menu: (provided, state) => ({
        ...provided,
        background: "#cdcecd",
        boxSizing: "border-box",
        boxShadow: "none",
        borderRadius: "10px",
        fontSize: "12px",
        fontWeight: 400,
        zIndex: 11,
        width: "auto",
        minWidth: "100%",
        "&:before": {
            content: '""',
            position: "absolute",
            top: "-12px",
            left: "10%",
            border: "6px solid transparent",
            borderBottom: "6px solid #cdcecd"
        }
    }),
    menuList: (base) => ({
        ...base,
        maxHeight: "150px",
        overflowX: "hidden",
        overflowY: "auto",
  
        "::-webkit-scrollbar": {
            width: "7px",
        },
        "::-webkit-scrollbar-track": {
            background: "#45a2d6",
            borderRadius: '10px',
        },
        "::-webkit-scrollbar-thumb": {
            background: "#3e3e3e",
            borderRadius: '10px',
        },
        "::-webkit-scrollbar-thumb:hover": {
            background: "#000",
        }
    }),
    option: (base) => ({
        ...base,
        color: "#3e3e3e",
        fontSize: "12px",
        textTransform: "uppercase",
        padding: "5px 20px",
        margin: "0 !important",
        background: "transparent",
        "&:hover": {
            backgroundColor: "#45a2d6",
            color: "#fafafa",
            cursor: "pointer"
        }
    }),
}
class DropdownSelector extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        this.props.onChanged(event);
    }

    render() {

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

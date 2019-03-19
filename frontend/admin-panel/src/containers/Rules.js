import React from 'react';
import ActionList from '../components/ActionList';
import FilterList from '../components/FilterList';
import Button from '@material-ui/core/Button';
import {getRules} from '../api/Api';

export default class Rules extends React.Component {

    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.state = {
            actions: props.actions || {},
            filters: props.filters || {},
            shouldUpdateProps: true
        }

    }

    componentDidMount() {
        if (window.slug && this.props.doRequest === undefined) {
            getRules(window.slug)
            .then(result => {
                this.setState({
                    actions: result.actions,
                    filters: result.filters
                })
            })
        }
    }

    handleClick(event) {
        if (window.slug) {
            this.props.history.push(`/${window.slug}`);
        }
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (this.props.doRequest !== undefined && this.state.shouldUpdateProps) {
            this.setState({
                actions: nextProps.actions,
                filters: nextProps.filters,
                shouldUpdateProps: false
            })
        }
        return true;
    }

    render() {
        return (
            <div>
                {
                    window.slug ? (
                        <div>
                            <h1 className="RulesHeading">Rules</h1>
                            <ActionList actions={this.state.actions}/>
                            <FilterList filters={this.state.filters}/>
                            <Button onClick={this.handleClick}>Edit rules</Button>
                        </div>
                    ) : false
                }
            </div>
        )
    }
}

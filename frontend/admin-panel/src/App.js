import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import logo from './logo.svg';
import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Actions';

class App extends Component {

  constructor(props) {
    super(props);

    this.handleClose = this.handleClose.bind(this);
    this.onChangeProps = this.onChangeProps.bind(this);
    this.putRules = this.putRules.bind(this);

    let { slug } = this.props.match.params;
    this.slug = slug;

    this.state = {
      open: true,
      actions: [],
      filters: {},
      eventTypes: []
    }
  }

  handleClose() {
    this.props.history.goBack();
  }

  onChangeProps(propName, propValue) {
    let state = {};
    state[propName] = propValue;
    this.setState(state)
  }

  getRules() {
    fetch(
      `http://localhost:9000/api/v0/badge-rules/?slug=${this.slug}`
      )
    .then(res => res.json())
    .then(result => {
        let actions = [];
        let eventTypes = [];

        for (let key in result.actions) {
            actions.push(
                {
                    id: Math.random(),
                    action: key,
                    count: result.actions[key]
                }
            )
        }
        for (let key in result.event_types) {
            eventTypes.push(result.event_types[key]["event_type"])
        }
        this.setState({
            actions: actions,
            filters: result.filters,
            eventTypes: eventTypes
        })
    },
    error => {
        console.log(error);
    })
  }

  putRules() {
    const rules = {}
    if (this.state.actions.length) {
      let validActions = this.state.actions.filter((action, ind) => {
          return action.count && action.action
      });
      const actions = {};
      validActions.map((el) => {
          actions[el.action] = +el.count;
      });
      rules.actions = actions;
      rules.filters = this.state.filters;
      console.log(rules);
  } else {
      alert('You havent choosen anything!');
  }
  }

  componentDidMount() {
      this.getRules();
  }

  render() {
    return (
      <Dialog open={this.state.open} >
        <DialogContent>
          <Actions {...this.state} onChangeProps={this.onChangeProps} putRules={this.putRules} slug={this.slug}/>
        </DialogContent>
        <DialogActions>
        <Button onClick={this.handleClose} color="primary">
              Close
            </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

export default App;

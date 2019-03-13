import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import logo from './logo.svg';
import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Action';

class App extends Component {

  constructor(props) {
    super(props);

    this.handleClose = this.handleClose.bind(this);
    this.onChangeProps = this.onChangeProps.bind(this);

    this.state = {
      open: true,
      actions: [],
      filters: {},
      eventTypes: []
    }
  }

  handleClose() {
    this.setState({
      open: !this.state.open
    })
  }

  onChangeProps(propName, propValue) {
    let state = {};
    state[propName] = propValue;
    this.setState(state)
  }

  getRules() {
    fetch('http://localhost:9000/api/v0/badge-rules/?slug=performance')
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

  componentDidMount() {
      this.getRules();
  }

  render() {
    return (
      <Dialog open={this.state.open} >
        <DialogContent>
          <Actions {...this.state} onChangeProps={this.onChangeProps}/>
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

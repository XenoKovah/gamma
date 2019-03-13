import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';
import FormControl from '@material-ui/core/FormControl';

import logo from './logo.svg';
import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Actions';
import Filter from './containers/Filter';

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

class App extends Component {

  constructor(props) {
    super(props);

    this.handleClose = this.handleClose.bind(this);
    this.onChangeProps = this.onChangeProps.bind(this);
    this.putRules = this.putRules.bind(this);
    this.onChangeFilter = this.onChangeFilter.bind(this);

    let { slug } = this.props.match.params;
    this.slug = slug;

    this.state = {
      open: true,
      actions: [],
      filters: {
        org: "",
        interval: {
          start: new Date(),
          end: new Date()
        },
        frequency: 0
      },
      eventTypes: []
    }
  }

  handleClose() {
    this.props.history.push("/");
  }

  onChangeProps(propName, propValue) {
    let state = {};
    state[propName] = propValue;
    this.setState(state)
  }

  getRules() {
    fetch(
      `/api/v0/badge-rules/?slug=${this.slug}`, {credentials: "same-origin"}
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
      fetch('/api/v0/badge-rules/', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({slug: this.slug, ...rules},
        {credentials: "same-origin"})
      }).then(response => response.json()).catch(error => console.log(error));
  } else {
      alert('You havent choosen anything!');
  }
  }

  componentDidMount() {
      this.getRules();
  }

  onChangeFilter(key, value) {
    let filters = this.state.filters;
    switch(key) {
      case 'start':
        filters.interval[key] = value;
        break;
      case 'end':
        filters.interval[key] = value;
        break;
      default:
        filters[key] = value;
    }
    this.setState({filters: filters});
    console.log('onChangeFilter', key, value, filters);
  }

  render() {
    return (
      <Dialog open={this.state.open} >
        <DialogContent>
            <Filter {...this.state.filters} onChange={this.onChangeFilter}/>
          <hr/>
          <Actions {...this.state} onChangeProps={this.onChangeProps} putRules={this.putRules} slug={this.slug}/>
        </DialogContent>
        <DialogActions>
        <Button onClick={this.putRules} size="large" color="primary">Save</Button>
        <Button size="large" color="primary">Delete</Button>
        <Button onClick={this.handleClose} color="primary">
              Close
            </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

export default App;

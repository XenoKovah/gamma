import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Button from '@material-ui/core/Button';

import logo from './logo.svg';
import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Actions';
import FilterContainer from './containers/FilterContainer';

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
    this.filtersChanged = this.filtersChanged.bind(this);
    this.getIndex = this.getIndex.bind(this);

    let { slug } = this.props.match.params;
    this.slug = slug;

    this.state = {
      open: true,
      actions: [],
      filters: [],
      eventTypes: []
    }
  }

  getIndex(conditions, id) {
    let index;
    conditions.map((el, ind) => {
        if (el.id === id) {
            index = ind;
        }
    });
    return index;
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
      `http://localhost:9000/api/v0/badge-rules/?slug=${this.slug}`, {credentials: "same-origin"}
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
        let filters = result.filters.map((filter, ind) => {
          filter.id = Math.random();
          return filter;
        })
        this.setState({
            actions: actions,
            filters: filters,
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

      fetch('http://localhost:9000/api/v0/badge-rules/', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({slug: this.slug, ...rules},
        {credentials: "same-origin"})
      }).then(response => {
        if (response.status == 200) {
          this.handleClose();
        }
        return response.json();
      }).catch(error => console.log(error));
  } else {
      alert('You havent choosen anything!');
  }
  }

  componentDidMount() {
      this.getRules();
  }

  filtersChanged(filters) {
    console.log('filtersChanged', filters);
    this.setState({filters: filters})
  }

  render() {
    return (
      <Dialog open={this.state.open} fullScreen={true} >
        <DialogContent>
          <div className="FilterContainer">
            <FilterContainer  filters={this.state.filters} filtersChanged={this.filtersChanged} getIndex={this.getIndex}/>
          </div>
          <Button size="small" variant="contained" color="primary">Add new filter</Button>
          <hr/>
          <Actions {...this.state} getIndex={this.getIndex} onChangeProps={this.onChangeProps} putRules={this.putRules} slug={this.slug}/>
        </DialogContent>
        <DialogActions>
        <Button onClick={this.putRules} size="large" color="primary">Save</Button>
        <Button onClick={this.handleClose} color="primary">
              Close
            </Button>
        </DialogActions>
      </Dialog>
    );
  }
}

export default App;

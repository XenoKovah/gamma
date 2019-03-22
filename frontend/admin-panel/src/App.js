import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { BADGE_RULES } from './api/Api';

import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Actions';
import FilterContainer from './containers/FilterContainer';
import Rules from './containers/Rules';
import { getCookie, isObjectEmpty} from './Utils';
import {getRules} from './api/Api';



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
      filters: {},
      emptyFilters: [],
      rawActions: {}
    }
  }

  getIndex(conditions, id) {
    let index;
    conditions.forEach((el, ind) => {
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
    getRules(this.slug)
    .then(result => {
        let actions = [];

        for (let key in result.actions) {
            actions.push(
                {
                    id: Math.random(),
                    action: key,
                    count: result.actions[key]
                }
            )
        };
        this.setState({
            actions: actions,
            filters: result.filters,
            rawActions: result.actions,
            shouldFilterUpdate: true
        })
    },
    error => {
        console.log(error);
    })
  }

  putRules() {
    const rules = {};
    if (!isObjectEmpty(this.state.actions) || !isObjectEmpty(this.state.filters)) {
      let validActions = this.state.actions.filter((action, ind) => {
          return action.count && action.action
      });
      const actions = {};
      validActions.forEach((el) => {
          actions[el.action] = +el.count;
      });
      rules.actions = actions;
      rules.filters = this.state.filters;

      fetch(BADGE_RULES, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken')},
        body: JSON.stringify({slug: this.slug, ...rules},
        {credentials: "same-origin"})
      }).then(response => {
        if (response.status === 200) {
          this.handleClose();
        }
        return response.json();
      }).catch(error => alert(error));
  }
  }

  componentDidMount() {
      this.getRules();
  }

  filtersChanged(filters) {
    this.setState({filters: filters})
  }

  render() {
    return (
      <div>
        <Rules doRequest={false} filters={this.state.filters} actions={this.state.rawActions}/>
        <Dialog open={this.state.open} maxWidth="xl" className="Dialog">
          <DialogTitle className="Dialog-Title"> Rules for "{this.slug}"</DialogTitle>
          <DialogContent className="Dialog-Content">
            <div className="Container">
              <div className="Container-Item">
                <Actions {...this.state} getIndex={this.getIndex} onChangeProps={this.onChangeProps} putRules={this.putRules} slug={this.slug}/>
              </div>
              <div className="Container-Item">
                <FilterContainer  filters={this.state.filters} shouldFilterUpdate={this.state.shouldFilterUpdate} filtersChanged={this.filtersChanged} getIndex={this.getIndex}/>
              </div>
            </div>
            <div className="Action_general">
              <button onClick={this.putRules} className="Btn Btn_primary Btn_general">Save</button>
              <button onClick={this.handleClose} className="Btn Btn_info Btn_general">Close</button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    );
  }
}

export default App;

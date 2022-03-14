import React, { Component } from 'react';
import Dialog from '@material-ui/core/Dialog';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { BADGE_RULES, getRules } from './api/Api';

import './App.css';

import 'react-dropdown/style.css';

import Actions from './containers/Actions';
import FilterContainer from './containers/FilterContainer';
import Rules from './containers/Rules';
import { getCookie, isObjectEmpty} from './Utils';

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
      badges: [],
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
    this.setState(state);
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
                    value: result.actions[key]
                }
            )
        };
        if (result.status_badge) {
            actions.push(
                {
                    id: Math.random(),
                    action: 'status_badge',
                    value: result.status_badge
                }
            )
        }
        if(result.badges){
            for (let badge of result.badges) {
                actions.push(
                    {
                        id: Math.random(),
                        action: 'badge',
                        value: badge
                    }
                )
            }
        }
        let filters = result.filters;
        if (filters && filters.interval && filters.interval.start && filters.interval.end) {
            // Add local timezone shift to avoid date shift due to interval values are stored with UTC timezone
            let start = new Date(filters.interval.start);
            let end = new Date(filters.interval.end);
            start.setMinutes( start.getMinutes() + start.getTimezoneOffset());
            end.setMinutes( end.getMinutes() + end.getTimezoneOffset());
            filters.interval.start = start;
            filters.interval.end = end;
        }
        this.setState({
            actions: actions,
            filters: filters,
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
          return action.value && action.action
      });
      const actions = {};
      const badges = [];
      const status_badge = null;

      for (let el of validActions){
        if(el.action === 'badge'){
            badges.push(el.value);
        }
        else if(el.action === 'status_badge'){
            rules.status_badge = el.value;
        }
        else{
            actions[el.action] = el.value;
        }
      }

      rules.actions = actions;
      if(badges.length > 0){
        rules.badges = badges;
      }
      rules.filters = this.state.filters;
      if (rules.filters && rules.filters.interval) {
          // Remove user timezone and send interval in UTC time,
          // set time for the start of the interval to be start of of the day
          // and end of the interval to be end of of the day.
          let start = rules.filters.interval.start;
          let end = rules.filters.interval.end;
          start.setHours(0, -1 * start.getTimezoneOffset(), 0, 0);
          end.setHours(23, 59 - end.getTimezoneOffset(), 59, 999);
          rules.filters.interval.start = start.toISOString();
          rules.filters.interval.end = end.toISOString();
      }

      (!rules.filters.frequency || rules.filters.frequency == '0') && delete rules.filters.frequency

      fetch(process.env.REACT_APP_LOCALHOST + BADGE_RULES, {
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
                <FilterContainer filters={this.state.filters} shouldFilterUpdate={this.state.shouldFilterUpdate} filtersChanged={this.filtersChanged} getIndex={this.getIndex}/>
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

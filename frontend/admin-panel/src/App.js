import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Dropdown from 'react-dropdown';
import 'react-dropdown/style.css';

import Action from './containers/Action';

class App extends Component {
  render() {
    return (
      <div className="Wrapper">
        <Action/>
      </div>
    );
  }
}

export default App;

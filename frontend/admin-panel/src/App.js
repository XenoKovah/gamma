import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Dropdown from 'react-dropdown';
import 'react-dropdown/style.css';

import Filter from './containers/Filter';

class App extends Component {
  render() {
    return (
      <div className="Wrapper">
        <Filter/>
      </div>
    );
  }
}

export default App;

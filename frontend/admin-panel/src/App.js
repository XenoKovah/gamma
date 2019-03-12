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

    this.state = {
      open: true
    }
  }

  handleClose() {
    this.setState({
      open: !this.state.open
    })
  }

  render() {
    return (
      <Dialog open={this.state.open} >
        <DialogContent>
          <Actions/>
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

import React from 'react';
import { Route, Link, HashRouter, BrowserRouter as Router } from 'react-router-dom';
import createBrowserHistory from "history/createBrowserHistory";

import App from './App';

const customHistory = createBrowserHistory();

const routing = (
    <HashRouter>
      <div>
        <Route exact path="*/:slug" component={App} history={customHistory} />
      </div>
    </HashRouter>
  )

  export default routing;

import React from 'react';
import { Route, HashRouter } from 'react-router-dom';
import createBrowserHistory from "history/createBrowserHistory";

import App from './App';
import Rules from './containers/Rules';

const customHistory = createBrowserHistory();

const routing = (
  <HashRouter>
    <div>
        <Route exact path="/" component={Rules} history={customHistory} />
        <Route path="/:slug" component={App} history={customHistory} />
    </div>
  </HashRouter>
  )

  export default routing;

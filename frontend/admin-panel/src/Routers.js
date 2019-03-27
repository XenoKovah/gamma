import React from 'react';
import { Route, HashRouter } from 'react-router-dom';
import createBrowserHistory from "history/createBrowserHistory";

import App from './App';
import Rules from './containers/Rules';
import LeaderBoard from './containers/LeaderBoard';

const customHistory = createBrowserHistory();

const routing = (
  <HashRouter>
    <div>
        <Route exact path="/" component={Rules} history={customHistory} />
        <Route exact path="/edit-rules/:slug" component={App} history={customHistory} />
        <Route exact path="/leaderboard" component={LeaderBoard} history={customHistory} />
    </div>
  </HashRouter>
  )

  export default routing;

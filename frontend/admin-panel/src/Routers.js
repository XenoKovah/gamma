import React from 'react';
import { Route, HashRouter } from 'react-router-dom';
import createBrowserHistory from "history/createBrowserHistory";

import App from './App';
import Rules from './containers/Rules';
import LeaderBoard from './containers/LeaderBoard';
import MoreBadges from './containers/MoreBadges';
import MoreUserStatuses from './containers/MoreUserStatuses';

const customHistory = createBrowserHistory();

const routing = (
  <HashRouter>
    <div>
        <Route exact path="/" component={Rules} history={customHistory} />
        <Route exact path="/edit-rules/:slug" component={App} history={customHistory} />
        <Route exact path="/leaderboard" component={LeaderBoard} history={customHistory} />
        <Route exact path="/more/badges/:username" component={MoreBadges} history={customHistory} />
        <Route exact path="/more/user-statuses/:username" component={MoreUserStatuses} history={customHistory} />
    </div>
  </HashRouter>
  )

  export default routing;

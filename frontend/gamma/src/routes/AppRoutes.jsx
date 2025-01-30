import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';

import { Avatar as AvatarPage } from '../modules/avatar';
import { Badges as BadgesPage } from '../modules/badges';

const AppRoutes = () => (
  <Router basename="/gamma">
    <Routes>
      <Route exact path="/" element={<AvatarPage />} />
      <Route path="/badges" element={<BadgesPage />} />
    </Routes>
  </Router>
);

export default AppRoutes;

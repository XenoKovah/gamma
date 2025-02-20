import React from 'react';

import { ROUTES } from '../../routes';
import { Badges as BadgesPage } from '.';

/**
 * Route configuration for the Badges page.
 *
 * This file is auto-imported via Webpack's `require.context` in the global routing setup,
 * ensuring it is included dynamically without manual imports.
 *
 * @constant {Array<Object>} routes - Route definition for the Badges page.
 * @property {string} routes[].path - The route path.
 * @property {React.Element} routes[].element - The associated React component.
 */
const routes = [
  {
    path: ROUTES.BADGES,
    element: <BadgesPage />,
  },
];

export default routes;

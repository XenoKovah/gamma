import React from 'react';

import { Avatar as AvatarPage } from '.';

/**
 * Route configuration for the Avatar page.
 *
 * This file is auto-imported via Webpack's `require.context` in the global routing setup,
 * ensuring it is included dynamically without manual imports.
 *
 * @constant {Array<Object>} routes - Route definition for the Avatar page.
 * @property {string} routes[].path - The route path.
 * @property {React.Element} routes[].element - The associated React component.
 */
const routes = [
  {
    path: '/avatar',
    element: <AvatarPage />,
  },
];

export default routes;

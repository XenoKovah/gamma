import React from 'react';

import { ROUTES } from '../../routes';
import { Avatars as AvatarsPage } from '.';

/**
 * Route configuration for the Avatars settings page.
 *
 * This file is auto-imported via Webpack's `require.context` in the global routing setup,
 * ensuring it is included dynamically without manual imports.
 *
 * @constant {Array<Object>} routes - Route definition for the Avatars settings page.
 * @property {string} routes[].path - The route path.
 * @property {React.Element} routes[].element - The associated React component.
 */
const routes = [
  {
    path: ROUTES.AVATARS,
    element: <AvatarsPage />,
  },
];

export default routes;

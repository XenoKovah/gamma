/**
 * Dynamically requires all `routes.jsx` files from the `modules` directory.
 *
 * @constant {__WebpackModuleApi.RequireContext} requireModule
 * - Webpack's require.context function that loads all `routes.jsx` files.
 */
const requireModule = require.context('../modules', true, /routes\.jsx$/);

/**
 * Extracts and flattens the default exports from all matched route files.
 *
 * @constant {Array} allRoutes - An array of all routes imported from `routes.js` files.
 */
const allRoutes = requireModule
  .keys()
  .map((fileName) => requireModule(fileName).default)
  .flat();

export default allRoutes;

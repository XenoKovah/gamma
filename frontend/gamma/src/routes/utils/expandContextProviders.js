/**
 * Dynamically requires all `context.js` files from the `modules` directory.
 *
 * @constant {__WebpackModuleApi.RequireContext} requireModule
 */
const requireModule = require.context('../../modules', true, /context\/[^/]+\.jsx$/);

/**
 * Extracts and flattens the default exports from all matched context files.
 *
 * @constant {Array} allProviders - An array of all context providers imported from `context.js` files.
 */
const allProviders = requireModule.keys().map((fileName) => requireModule(fileName).default);

export default allProviders;

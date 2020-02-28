const common = require('./webpack.common.config.js');
const BundleTracker = require('webpack-bundle-tracker');
const Dotenv = require('dotenv-webpack');
const merge = require('webpack-merge');

module.exports = merge(common, {
  mode: 'production',
  devtool: 'source-map',
  plugins: [
    new BundleTracker({filename: './webpack-stats-prod.json'}),
    new Dotenv({
        path: './envs/base.env',
    }),
  ],
});

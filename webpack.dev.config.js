const common = require('./webpack.common.config.js');
const BundleTracker = require('webpack-bundle-tracker');
const Dotenv = require('dotenv-webpack');
const merge = require('webpack-merge');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'inline-source-map',
  plugins: [
    new BundleTracker({filename: './webpack-stats-dev.json'}),
    new Dotenv({
        path: './envs/webpack-dev.env',
    }),
  ],
});

const config = require('./webpack.dev.config.js');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const Dotenv = require('dotenv-webpack');

config.mode = 'production';
config.devtool = 'source-map';

config.plugins = [
    new CleanWebpackPlugin(),
    new BundleTracker({filename: './webpack-stats-prod.json'}),
    new MiniCssExtractPlugin({
        filename: '[name].[hash].css',
        chunkFilename: '[id].[hash].css',
    }),
    new Dotenv({
        path: './envs/prod.env',
    }),
];

module.exports = config;

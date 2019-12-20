const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const Dotenv = require('dotenv-webpack');

module.exports = {
    mode: 'development',
    entry: {
        admin_panel: './frontend/admin-panel/webpackGraph.js',
        core: './core/static/core/webpackGraph.js',
    },
    plugins: [
        new CleanWebpackPlugin(),
        new BundleTracker({filename: './webpack-stats-dev.json'}),
        new MiniCssExtractPlugin({
            filename: '[name].[hash].css',
            chunkFilename: '[id].[hash].css',
        }),
        new Dotenv({
            path: './envs/local.env',
        }),
    ],
    output: {
        path: path.resolve('./frontend/webpack_bundles/'),
        filename: '[name].[hash].js',
    },
    optimization: {
        moduleIds: 'hashed',
        runtimeChunk: 'single',
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all',
                },
            },
        },
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ['@babel/preset-react'],
                    }
                }
            },
            {
                test: /\.css$/,
                use: [
                      {
                        loader: MiniCssExtractPlugin.loader,
                      },
                    //'style-loader',
                    'css-loader',
                    'postcss-loader',
                ],
            },
            {
                test: /\.(woff|woff2|png|svg|jpg|gif)$/,
                use: [
                    'file-loader',
                ],
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                     {
                        loader: MiniCssExtractPlugin.loader,
                     },
                    // Creates `style` nodes from JS strings
                    // 'style-loader',
                    // Translates CSS into CommonJS
                    'css-loader',
                    // Compiles Sass to CSS
                    'sass-loader',
                ],
            },
            {
                test: /\.json$/,
                loader: "json-loader"
            },
        ],
    },
};

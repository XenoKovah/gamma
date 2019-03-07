var path = require('path');

module.exports = {
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader"
          }
        }
      ]
    },
    output: {
        path: path.resolve(__dirname, '../core/static/core/js/'),
        filename: 'bundle.js'
      }
  };

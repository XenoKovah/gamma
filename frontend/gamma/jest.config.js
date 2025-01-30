const path = require('path');
const presets = require('./lib/presets');

module.exports = {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '\\.svg': path.resolve(__dirname, 'jest/svgMock.js'),
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': path.resolve(__dirname, 'jest/fileMock.js'),
    '\\.(css|scss)$': 'identity-obj-proxy',
    'env.config': path.resolve(__dirname, 'jest/fallback.env.config.js'),
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(@edx|@openedx))',
  ],
  transform: {
    '^.+\\.[t|j]sx?$': [
      'babel-jest',
      { configFile: presets.babel.resolvedFilepath },
    ],
  },
  setupFiles: ['./src/setupTests.jsx'],
};

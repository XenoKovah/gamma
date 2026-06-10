// Pin the timezone before Jest spawns workers: formatDateToISO and friends
// format in local time, so date-part assertions (the interval-date-picker
// suites) are only deterministic in a fixed zone. RG's CI runs in UTC; match
// it. Setting this here (config loads in the main process) makes workers
// inherit TZ=UTC at process start, which works regardless of whether Node
// honors mid-process TZ changes.
process.env.TZ = 'UTC';

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

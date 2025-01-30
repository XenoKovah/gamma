const ConfigPreset = require('./ConfigPreset');

const searchFilepaths = [process.cwd()];

const babel = new ConfigPreset({
  defaultFilename: 'babel.config.js',
  searchFilenames: ['.babelrc', '.babelrc.js', 'babel.config.js'],
  searchFilepaths,
});

module.exports = { babel };

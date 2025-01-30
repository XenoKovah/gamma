const path = require('path');
const resolveFilepaths = require('./resolveFilepaths');

const defaultConfigDir = path.resolve(__dirname, '../config');

function ConfigPreset({
  defaultDir = defaultConfigDir,
  searchFilenames,
  searchFilepaths,
}) {
  return {
    get resolvedFilepath() {
      return resolveFilepaths(
        searchFilenames.map(filename => `./${filename}`),
        [...searchFilepaths, defaultDir],
      );
    },
  };
}

module.exports = ConfigPreset;

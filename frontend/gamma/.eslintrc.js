module.exports = {
  extends: '@edx/eslint-config',
  parser: '@babel/eslint-parser',
  parserOptions: {
    requireConfigFile: false,
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'import/no-extraneous-dependencies': [
      'error',
      {
        devDependencies: [
          '**/*.config.*',
          '**/*.test.*',
          '**/setupTests.jsx',
        ],
      },
    ],
    'import/no-unresolved': ['error'],
    // https://github.com/evcohen/eslint-plugin-jsx-a11y/issues/340#issuecomment-338424908
    'jsx-a11y/anchor-is-valid': ['error', {
      components: ['Link'],
      specialLink: ['to'],
    }],
    'import/no-import-module-export': 'off',
    'react/function-component-definition': [2, { namedComponents: 'arrow-function' }],
    'jsx-a11y/label-has-associated-control': [2, {
      controlComponents: ['Input'],
    }],
    'template-curly-spacing': 'off',
    'react-hooks/exhaustive-deps': 'off',
    'no-restricted-exports': 'off',
    // There is no reason to disallow this syntax anymore; we don't use regenerator-runtime in new browsers
    'no-restricted-syntax': 'off',
    'import/prefer-default-export': 'off',
  },
  globals: {
    newrelic: false,
  },
};

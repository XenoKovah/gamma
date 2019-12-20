module.exports = {
    presets: [
        '@babel/preset-env',
        '@babel/preset-react',
        '@babel/preset-flow',
    ],
    plugins: [
        '@babel/plugin-proposal-class-properties',
        '@babel/plugin-transform-modules-commonjs',
        '@babel/plugin-transform-react-jsx-source',
        '@babel/plugin-proposal-object-rest-spread',
    ],
};

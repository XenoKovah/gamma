module.exports = [
  {
    id: 101,
    title: 'Contributor Badge',
    description: 'Awarded for making valuable contributions to the community.',
    image: 'http://0.0.0.0:9700/media/uploads/contributor_badge.png',
    active: true,
    slug: 'contributor',
    rules: [
      {
        id: 1,
        action: {
          test: 'test',
        },
        filters: {
          test: 'test',
        },
      },
    ],
  },
  {
    id: 102,
    title: 'Bug Hunter',
    description: 'Earned by reporting and verifying at least 5 valid bugs.',
    image: 'http://0.0.0.0:9700/media/uploads/bug_hunter_badge.png',
    active: true,
    slug: 'bug-hunter',
    rules: [
      {
        id: 1,
        action: {
          test: 'test',
        },
        filters: {
          test: 'test',
        },
      },
    ],
  },
];

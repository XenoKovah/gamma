module.exports = [
  {
    id: 101,
    title: 'Contributor Badge',
    description: 'Awarded for making valuable contributions to the community.',
    image: 'http://0.0.0.0:9700/media/uploads/contributor_badge.png',
    is_active: true,
    slug: 'contributor',
    rules: [
      {
        id: 1,
        action: {
          count: 'test',
          eventType: 'count',
        },
        event_configuration: null,
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
    is_active: true,
    slug: 'bug-hunter',
    rules: [
      {
        id: 1,
        action: {
          count: 'test',
          eventType: 'count',
        },
        event_configuration: null,
        filters: {
          test: 'test',
        },
      },
    ],
  },
];

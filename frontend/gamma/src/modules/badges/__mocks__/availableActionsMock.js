module.exports = [
  {
    id: 1,
    eventName: 'edx_bookmark_added',
    title: 'Add bookmark',
    schema: [
      {
        field: 'count',
        title: 'Number of repetitions required',
        type: 'integer',
        required: true,
      },
    ],
  },
  {
    id: 3,
    eventName: 'rgg_points_distribution',
    title: 'Points Distribution',
    schema: [
      {
        field: 'points',
        title: 'Number of points required',
        type: 'integer',
        required: true,
      },
    ],
  },
];

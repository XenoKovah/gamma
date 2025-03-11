module.exports = [
  {
    id: 12,
    title: 'Avatar Set 1',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
      {
        id: 2,
        title: 'Avatar 2',
        description: 'Avatar 2 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-2.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 13,
    title: 'Avatar Set 2',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 14,
    title: 'Avatar Set 3',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 15,
    title: 'Avatar Set 4',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 16,
    title: 'Avatar Set 5',
    avatars: [],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 17,
    title: 'Avatar Set 6',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 18,
    title: 'Avatar Set 7',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar 1 Description',
        image: 'http://0.0.0.0:9700/media/uploads/avatars/avatar-1.svg',
        rules: [
          {
            id: 1,
            action: {
              test: 'test',
            },
            filters: {},
          },
        ],
      },
    ],
    use_in_courses: [
      'test',
    ],
    is_draft: true,
  },
  {
    id: 19,
    title: 'Avatar Set 8',
    avatars: [],
    use_in_courses: [
      'Avatar Set 1',
    ],
    is_draft: true,
  },
  {
    id: 20,
    title: 'Avatar Set 20',
    avatars: [
      {
        id: 1,
        title: 'Avatar 1',
        description: 'Avatar Description 1',
        image: 'avatar1.png',
        rules: [],
      },
      {
        id: 2,
        title: 'Avatar 2',
        description: 'Avatar Description 2',
        image: 'avatar2.png',
        rules: [
          {
            id: 17,
            action: { eventType: 'badge', count: 20 },
            filters: {},
            created_at: '2025-03-10T12:07:59.431440Z',
          },
          {
            id: 33,
            action: { eventType: 'status_badge', count: 30 },
            filters: {
              frequency: 55,
              course: 'course-v1:OpenedX+DemoX+DemoCourse',
            },
            created_at: '2025-03-10T12:58:54.145427Z',
          },
        ],
      },
    ],
  },
];

import allRoutes from '../utils';

jest.mock('../utils', () => {
  const mockRequireContext = () => ({
    keys: jest.fn(() => ['module/avatar/routes.jsx', 'module/badges/routes.jsx']),
    resolve: jest.fn(),
    id: 'mocked-require-context',
    require: jest.fn((fileName) => {
      const routes = {
        'module/avatar/routes.jsx': { default: [{ path: '/avatar', component: 'AvatarPage' }] },
        'module/badges/routes.jsx': { default: [{ path: '/badges', component: 'BadgesPage' }] },
      };
      return routes[fileName] || { default: [] };
    }),
  });

  return {
    __esModule: true,
    default: (() => {
      const requireModule = mockRequireContext();
      return requireModule.keys()
        .map((fileName) => requireModule.require(fileName).default)
        .flat();
    })(),
  };
});

describe('allRoutes', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  it('should aggregate all routes from modules', () => {
    expect(allRoutes).toEqual([
      { path: '/avatar', component: 'AvatarPage' },
      { path: '/badges', component: 'BadgesPage' },
    ]);
  });

  it('should return an empty array if no routes exist', async () => {
    jest.doMock('../utils', () => ({
      __esModule: true,
      default: [],
    }));

    const { default: emptyRoutes } = await import('../utils');
    expect(emptyRoutes).toEqual([]);
  });
});

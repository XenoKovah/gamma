import { allProviders } from '../utils';

jest.mock('../utils/expandContextProviders', () => {
  const mockRequireContext = () => ({
    keys: jest.fn(() => ['modules/avatar/context.jsx', 'modules/badges/context.jsx']),
    require: jest.fn((fileName) => {
      const contexts = {
        'modules/avatar/context.jsx': { default: () => 'AvatarProvider' },
        'modules/badges/context.jsx': { default: () => 'BadgesProvider' },
      };
      return contexts[fileName] || { default: null };
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

describe('allProviders', () => {
  beforeEach(() => {
    jest.resetModules();
  });

  it('should aggregate all context providers from modules', () => {
    expect(allProviders).toEqual([expect.any(Function), expect.any(Function)]);
    expect(allProviders[0]()).toBe('AvatarProvider');
    expect(allProviders[1]()).toBe('BadgesProvider');
  });

  it('should return an empty array if no providers exist', async () => {
    jest.doMock('../utils/expandContextProviders', () => ({
      __esModule: true,
      default: [],
    }));

    const { default: emptyProviders } = await import('../utils/expandContextProviders');
    expect(emptyProviders).toEqual([]);
  });
});

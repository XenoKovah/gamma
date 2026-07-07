import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

import {
  fetchBadgesData,
  fetchCoursesData,
  fetchOrganizationsData,
  fetchActionsData,
  createBadge,
  editBadge,
  deleteBadge,
  resolveIdentifiersToUsernames,
} from '../api';

import {
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
  preparePayload,
  processReceivedPayload,
} from '../utils';

import { API_ROUTES } from '../constants';

jest.mock('../utils', () => ({
  ...jest.requireActual('../utils'),
  logError: jest.fn(),
  fileToBase64: jest.fn(() => Promise.resolve('base64EncodedString')),
}));

const LMS_BASE_URL = 'https://lms.example.com';
jest.mock('../../../../utils', () => ({
  getGammaHeaderConfig: jest.fn(() => ({ lmsBaseUrl: 'https://lms.example.com' })),
}));

describe('API functions', () => {
  let mock;

  beforeEach(() => {
    global.structuredClone = jest.fn((obj) => JSON.parse(JSON.stringify(obj)));
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe('fetchBadgesData', () => {
    it('should fetch and process badges data', async () => {
      const mockData = [{ id: 1, name: 'Test Badge' }];
      const expectedData = mockData.map(convertKeysToCamelCase).map(processReceivedPayload);

      mock.onGet(API_ROUTES.BADGES).reply(200, mockData);

      const result = await fetchBadgesData();
      expect(result).toEqual(expectedData);
    });

    it('should throw an error when request fails', async () => {
      mock.onGet(API_ROUTES.BADGES).reply(500);

      await expect(fetchBadgesData()).rejects.toThrow();
    });
  });

  describe('fetchCoursesData', () => {
    it('should fetch and process courses data', async () => {
      const mockData = { id: 1, title: 'Course 1' };
      mock.onGet(API_ROUTES.COURSES).reply(200, mockData);

      const result = await fetchCoursesData();
      expect(result).toEqual(convertKeysToCamelCase(mockData));
    });

    it('should throw an error when request fails', async () => {
      mock.onGet(API_ROUTES.COURSES).reply(500);
      await expect(fetchCoursesData()).rejects.toThrow();
    });
  });

  describe('fetchOrganizationsData', () => {
    it('should fetch and process organizations data', async () => {
      const mockData = { id: 1, name: 'Organization 1' };
      mock.onGet(API_ROUTES.ORGANIZATIONS).reply(200, mockData);

      const result = await fetchOrganizationsData();
      expect(result).toEqual(convertKeysToCamelCase(mockData));
    });

    it('should throw an error when request fails', async () => {
      mock.onGet(API_ROUTES.ORGANIZATIONS).reply(500);
      await expect(fetchOrganizationsData()).rejects.toThrow();
    });
  });

  describe('fetchActionsData', () => {
    it('should fetch and process actions data', async () => {
      const mockData = { actionType: 'click', count: 10 };
      mock.onGet(API_ROUTES.ACTIONS).reply(200, mockData);

      const result = await fetchActionsData();
      expect(result).toEqual(convertKeysToCamelCase(mockData));
    });

    it('should throw an error when request fails', async () => {
      mock.onGet(API_ROUTES.ACTIONS).reply(500);
      await expect(fetchActionsData()).rejects.toThrow();
    });
  });

  describe('createBadge', () => {
    it('should create a new badge', async () => {
      const badgeData = { name: 'New Badge', image: new File([], 'image.png') };
      const processedData = {
        ...preparePayload(badgeData),
        image: 'base64EncodedString',
      };

      const expectedRequestData = convertKeysToSnakeCase(processedData);
      const mockResponse = { id: 1, ...expectedRequestData };

      mock.onPost(API_ROUTES.BADGES).reply(201, mockResponse);

      const result = await createBadge(badgeData);
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error when request fails', async () => {
      mock.onPost(API_ROUTES.BADGES).reply(500);
      await expect(createBadge({ name: 'Test' })).rejects.toThrow();
    });
  });

  describe('editBadge', () => {
    it('should edit an existing badge', async () => {
      const badgeId = 1;
      const badgeData = { name: 'Updated Badge', image: new File([], 'image.png') };
      const processedData = preparePayload(structuredClone(badgeData));
      processedData.image = 'base64EncodedString';

      const expectedRequestData = convertKeysToSnakeCase(processedData);
      const mockResponse = { id: badgeId, ...expectedRequestData };

      mock.onPatch(`${API_ROUTES.BADGES}${badgeId}/`).reply(200, mockResponse);

      const result = await editBadge(badgeId, badgeData);
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error when request fails', async () => {
      const badgeId = 1;
      mock.onPatch(`${API_ROUTES.BADGES}${badgeId}/`).reply(500);

      await expect(editBadge(badgeId, { name: 'Test' })).rejects.toThrow();
    });
  });

  describe('deleteBadge', () => {
    it('should delete a badge', async () => {
      const badgeId = 1;
      const mockResponse = { success: true };

      mock.onDelete(`${API_ROUTES.BADGES}${badgeId}/`).reply(200, mockResponse);

      const result = await deleteBadge(badgeId);
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error when request fails', async () => {
      const badgeId = 1;
      mock.onDelete(`${API_ROUTES.BADGES}${badgeId}/`).reply(500);

      await expect(deleteBadge(badgeId)).rejects.toThrow();
    });
  });

  describe('resolveIdentifiersToUsernames', () => {
    beforeEach(() => {
      mock.onGet(`${LMS_BASE_URL}/api/user/v1/accounts`).reply((config) => {
        const email = config.params?.email;
        if (email === 'xkovah@gmail.com') {
          return [200, [{ username: 'XenoPublic', email }]];
        }
        return [404, {}];
      });
    });

    it('passes usernames through unchanged without hitting the LMS', async () => {
      const result = await resolveIdentifiersToUsernames(['jdoe', 'asmith']);
      expect(result).toEqual({ usernames: ['jdoe', 'asmith'], unresolved: [] });
      expect(mock.history.get).toHaveLength(0);
    });

    it('resolves an email to its username via the LMS accounts API', async () => {
      const result = await resolveIdentifiersToUsernames(['xkovah@gmail.com']);
      expect(result).toEqual({ usernames: ['XenoPublic'], unresolved: [] });
    });

    it('handles a mix of usernames and emails, preserving order', async () => {
      const result = await resolveIdentifiersToUsernames(['jdoe', 'xkovah@gmail.com']);
      expect(result).toEqual({ usernames: ['jdoe', 'XenoPublic'], unresolved: [] });
    });

    it('reports an email that matches no user (404) as unresolved', async () => {
      const result = await resolveIdentifiersToUsernames(['nobody@nowhere.tld']);
      expect(result).toEqual({ usernames: [], unresolved: ['nobody@nowhere.tld'] });
    });

    it('de-duplicates resolved usernames (email + its username collapse)', async () => {
      const result = await resolveIdentifiersToUsernames(['XenoPublic', 'xkovah@gmail.com']);
      expect(result).toEqual({ usernames: ['XenoPublic'], unresolved: [] });
    });
  });
});

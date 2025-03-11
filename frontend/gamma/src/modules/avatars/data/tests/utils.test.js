import axios from 'axios';
import {
  readFileAsBase64,
  fetchImageAsBlob,
  convertImageToBase64,
  transformActions,
  preparePayload,
  getCsrfToken,
  toCamelCase,
  toSnakeCase,
  reverseTransformActions,
  processReceivedAvatarSets,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
} from '../utils';

jest.mock('axios');

describe('Utility functions', () => {
  describe('readFileAsBase64', () => {
    it('should convert a File to Base64', async () => {
      const mockFile = new Blob(['test'], { type: 'text/plain' });
      const result = await readFileAsBase64(mockFile);
      expect(result).toMatch(/^data:text\/plain;base64,/);
    });
  });

  describe('fetchImageAsBlob', () => {
    it('should fetch an image as a blob', async () => {
      const mockBlob = new Blob(['image'], { type: 'image/png' });
      axios.get.mockResolvedValue({ data: mockBlob });

      const result = await fetchImageAsBlob('https://example.com/image.png');
      expect(result).toBeInstanceOf(Blob);
    });
  });

  describe('convertImageToBase64', () => {
    it('should return the same base64 string if already in correct format', async () => {
      const base64Image = 'data:image/png;base64,abcd1234';
      const result = await convertImageToBase64(base64Image);
      expect(result).toBe(base64Image);
    });

    it('should convert a Blob to Base64', async () => {
      const mockBlob = new Blob(['image'], { type: 'image/png' });
      const result = await convertImageToBase64(mockBlob);
      expect(result).toMatch(/^data:image\/png;base64,/);
    });
  });

  describe('transformActions and reverseTransformActions', () => {
    it('should transform actions correctly', () => {
      const rules = [{ action: { eventType: 'click', count: 2 } }];
      const transformed = transformActions(rules);
      expect(transformed).toEqual([{ action: { click: 2 } }]);
    });

    it('should reverse transform actions correctly', () => {
      const rules = [{ action: { click: 2 } }];
      const reversed = reverseTransformActions(rules);
      expect(reversed).toEqual([{ action: { eventType: 'click', count: 2 } }]);
    });
  });

  describe('preparePayload', () => {
    it('should remove temp IDs and transform actions', () => {
      const data = { rules: [{ action: { eventType: 'click', count: 2 } }] };
      const transformed = preparePayload(data);
      expect(transformed).toEqual({ rules: [{ action: { click: 2 } }] });
    });
  });

  describe('getCsrfToken', () => {
    it('should return the CSRF token if found', () => {
      Object.defineProperty(document, 'cookie', {
        value: 'csrftoken=abc123; othercookie=value',
        writable: true,
      });
      expect(getCsrfToken()).toBe('abc123');
    });
  });

  describe('Case conversion functions', () => {
    it('should convert snake_case to camelCase', () => {
      expect(toCamelCase('snake_case_string')).toBe('snakeCaseString');
    });

    it('should convert camelCase to snake_case', () => {
      expect(toSnakeCase('camelCaseString')).toBe('camel_case_string');
    });
  });

  describe('convertKeysToCamelCase and convertKeysToSnakeCase', () => {
    it('should recursively convert object keys to camelCase', () => {
      const input = { first_name: 'John', last_name: 'Doe', user_info: { profile_image: 'url' } };
      const output = convertKeysToCamelCase(input);
      expect(output).toEqual({ firstName: 'John', lastName: 'Doe', userInfo: { profileImage: 'url' } });
    });

    it('should recursively convert object keys to snake_case', () => {
      const input = { firstName: 'John', lastName: 'Doe', userInfo: { profileImage: 'url' } };
      const output = convertKeysToSnakeCase(input);
      expect(output).toEqual({ first_name: 'John', last_name: 'Doe', user_info: { profile_image: 'url' } });
    });
  });

  describe('processReceivedAvatarSets', () => {
    it('should process avatar sets and reverse transform rules', () => {
      const avatarSets = [{ avatars: [{ rules: [{ action: { click: 2 } }] }] }];
      const result = processReceivedAvatarSets(avatarSets);
      expect(result).toEqual([{ avatars: [{ rules: [{ action: { eventType: 'click', count: 2 } }] }] }]);
    });
  });
});

import {
  getCsrfToken,
  fileToBase64,
  transformActions,
  reverseTransformActions,
  preparePayload,
  processReceivedPayload,
  toCamelCase,
  toSnakeCase,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
  logError,
} from '../utils';

describe('getCsrfToken', () => {
  it('should return the CSRF token if present in cookies', () => {
    Object.defineProperty(document, 'cookie', {
      value: 'csrftoken=abc123; othercookie=value',
      writable: true,
    });
    expect(getCsrfToken()).toBe('abc123');
  });

  it('should return an empty string if CSRF token is not found', () => {
    Object.defineProperty(document, 'cookie', {
      value: 'othercookie=value',
      writable: true,
    });
    expect(getCsrfToken()).toBe('');
  });
});

describe('fileToBase64', () => {
  it('should convert a file to a Base64 string', async () => {
    const file = new File(['hello'], 'test.txt', { type: 'text/plain' });

    const result = await fileToBase64(file);
    expect(result).toMatch(/^data:text\/plain;base64,/);
  });
});

describe('transformActions & reverseTransformActions', () => {
  const rules = [
    { id: 1, action: { eventType: 'click', count: 5 }, eventConfiguration: null },
    { id: 2, action: { eventType: 'hover', count: 2 }, eventConfiguration: null },
  ];

  it('should transform actions correctly', () => {
    const transformed = transformActions(rules);
    expect(transformed).toEqual([
      { id: 1, action: { click: 5 }, eventConfiguration: null },
      { id: 2, action: { hover: 2 }, eventConfiguration: null },
    ]);
  });

  it('should reverse transform actions correctly', () => {
    const transformed = transformActions(rules);
    const reversed = reverseTransformActions(transformed);
    expect(reversed).toEqual(rules);
  });
});

describe('preparePayload & processReceivedPayload', () => {
  const inputData = {
    rules: [
      { id: 1, action: { eventType: 'click', count: 3 }, eventConfiguration: null },
    ],
  };

  it('should prepare the payload correctly', () => {
    const result = preparePayload(inputData);
    expect(result).toEqual({
      rules: [{ id: 1, action: { click: 3 }, eventConfiguration: null }],
    });
  });

  it('should process received payload correctly', () => {
    const transformedData = preparePayload(inputData);
    const result = processReceivedPayload(transformedData);
    expect(result).toEqual(inputData);
  });
});

describe('toCamelCase & toSnakeCase', () => {
  it('should convert snake_case to camelCase', () => {
    expect(toCamelCase('hello_world')).toBe('helloWorld');
    expect(toCamelCase('user_id')).toBe('userId');
  });

  it('should convert camelCase to snake_case', () => {
    expect(toSnakeCase('helloWorld')).toBe('hello_world');
    expect(toSnakeCase('userId')).toBe('user_id');
  });
});

describe('convertKeysToCamelCase & convertKeysToSnakeCase', () => {
  const inputObject = {
    first_name: 'John',
    last_name: 'Doe',
    user_info: {
      phone_number: '123456789',
    },
  };

  it('should convert object keys to camelCase', () => {
    expect(convertKeysToCamelCase(inputObject)).toEqual({
      firstName: 'John',
      lastName: 'Doe',
      userInfo: { phoneNumber: '123456789' },
    });
  });

  it('should convert object keys to snake_case', () => {
    const camelCaseObject = convertKeysToCamelCase(inputObject);
    expect(convertKeysToSnakeCase(camelCaseObject)).toEqual(inputObject);
  });
});

describe('logError', () => {
  it('should log an error message', () => {
    // eslint-disable-next-line no-console
    console.error = jest.fn();
    logError('Test Error', new Error('Something went wrong'));

    // eslint-disable-next-line no-console
    expect(console.error).toHaveBeenCalledWith('Test Error', expect.any(Error));
  });
});

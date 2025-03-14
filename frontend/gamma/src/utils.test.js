import { getCookieByName, capitalizeFirstLetter } from './utils';

describe('getCookieByName', () => {
  beforeEach(() => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'user=JohnDoe; theme=dark; sessionToken=abc123',
    });
  });

  it('should return the correct cookie value if the cookie exists', () => {
    expect(getCookieByName('user')).toBe('JohnDoe');
    expect(getCookieByName('theme')).toBe('dark');
    expect(getCookieByName('sessionToken')).toBe('abc123');
  });

  it('should return null if the cookie does not exist', () => {
    expect(getCookieByName('nonExistentCookie')).toBeNull();
  });

  it('should decode URL-encoded cookie values', () => {
    document.cookie = `encodedValue=${ encodeURIComponent('hello world')}`;
    expect(getCookieByName('encodedValue')).toBe('hello world');
  });
});

describe('capitalizeFirstLetter', () => {
  it('should capitalize the first letter of a lowercase word', () => {
    expect(capitalizeFirstLetter('hello')).toBe('Hello');
  });

  it('should capitalize the first letter of a sentence', () => {
    expect(capitalizeFirstLetter('this is a test')).toBe('This is a test');
  });

  it('should not change an already capitalized string', () => {
    expect(capitalizeFirstLetter('Hello')).toBe('Hello');
  });

  it('should not affect strings where the first character is not a letter', () => {
    expect(capitalizeFirstLetter('123abc')).toBe('123abc');
    expect(capitalizeFirstLetter('@symbol')).toBe('@symbol');
  });

  it('should return an empty string if input is empty', () => {
    expect(capitalizeFirstLetter('')).toBe('');
  });

  it('should handle single-letter strings', () => {
    expect(capitalizeFirstLetter('a')).toBe('A');
    expect(capitalizeFirstLetter('z')).toBe('Z');
  });
});

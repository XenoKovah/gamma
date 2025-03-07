import { formatDateToISO } from '../utils';

describe('formatDateToISO', () => {
  it('should format a valid Date object to ISO 8601 format without milliseconds', () => {
    const date = new Date('2024-05-15T12:34:56.789Z');
    expect(formatDateToISO(date)).toBe('2024-05-15T12:34:56');
  });

  it('should return null for an invalid date object', () => {
    expect(formatDateToISO(new Date('invalid-date'))).toBeNull();
  });

  it('should return null when input is not a Date object', () => {
    expect(formatDateToISO(null)).toBeNull();
    expect(formatDateToISO(undefined)).toBeNull();
    expect(formatDateToISO(123456789)).toBeNull();
    expect(formatDateToISO('2024-05-15')).toBeNull();
    expect(formatDateToISO({})).toBeNull();
    expect(formatDateToISO([])).toBeNull();
  });

  it('should handle edge case of Unix epoch (1970-01-01T00:00:00Z)', () => {
    const date = new Date(0);
    expect(formatDateToISO(date)).toBe('1970-01-01T00:00:00');
  });
});

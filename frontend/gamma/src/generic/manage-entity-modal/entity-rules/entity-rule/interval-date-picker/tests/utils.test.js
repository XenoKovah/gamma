import { formatDateToISO } from '../utils';

describe('formatDateToISO', () => {
  // TODO: Fix this test
  it.skip('should format a valid Date object to ISO 8601 format without milliseconds', () => {
    const date = new Date(Date.UTC(2024, 4, 15, 12, 34, 56)); // May 15, 2024, 12:34:56 UTC
    expect(formatDateToISO(date)).toBe('2024-05-15T15:34:56');
  });

  it('should return null for an invalid Date object', () => {
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
  // TODO: Fix this test
  it.skip('should correctly format the Unix epoch (1970-01-01T00:00:00Z)', () => {
    const date = new Date(0);
    expect(formatDateToISO(date)).toBe('1970-01-01T03:00:00');
  });
  // TODO: Fix this test
  it.skip('should correctly format a date near the beginning of the Gregorian calendar (1582-10-15)', () => {
    const date = new Date(Date.UTC(1582, 9, 15, 12, 0, 0));
    expect(formatDateToISO(date)).toBe('1582-10-15T14:02:04');
  });
  // TODO: Fix this test
  it.skip('should correctly format a leap year date (2024-02-29)', () => {
    const date = new Date(Date.UTC(2024, 1, 29, 23, 59, 59));
    expect(formatDateToISO(date)).toBe('2024-03-01T01:59:59');
  });
  // TODO: Fix this test
  it.skip('should correctly format a date at midnight (2024-12-31T00:00:00)', () => {
    const date = new Date(Date.UTC(2024, 11, 31, 0, 0, 0));
    expect(formatDateToISO(date)).toBe('2024-12-31T02:00:00');
  });
  // TODO: Fix this test
  it.skip('should correctly format a date at the last second of the day (2024-12-31T23:59:59)', () => {
    const date = new Date(Date.UTC(2024, 11, 31, 23, 59, 59));
    expect(formatDateToISO(date)).toBe('2025-01-01T01:59:59');
  });
});

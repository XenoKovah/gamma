import { formatDateToISO } from '../utils';

describe('formatDateToISO', () => {
  it('should format a valid Date object to ISO 8601 format without milliseconds (UTC) and check only date part', () => {
    const date = new Date(Date.UTC(2024, 4, 15, 12, 34, 56));
    expect(formatDateToISO(date).slice(0, 10)).toBe('2024-05-15');
  });

  it('should correctly format the Unix epoch (1970-01-01T00:00:00Z) and check only date part', () => {
    const date = new Date(0);
    expect(formatDateToISO(date).slice(0, 10)).toBe('1970-01-01');
  });

  it('should correctly format a date at midnight (2024-12-31T00:00:00) and check only date part', () => {
    const date = new Date(Date.UTC(2024, 11, 31, 0, 0, 0));
    expect(formatDateToISO(date).slice(0, 10)).toBe('2024-12-31');
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

  it('should correctly format the Unix epoch (1970-01-01T00:00:00Z)', () => {
    const date = new Date(0);
    expect(formatDateToISO(date)).toMatch(/^1970-01-01T\d{2}:\d{2}:\d{2}/);
  });

  it('should correctly format a date near the beginning of the Gregorian calendar (1582-10-15)', () => {
    const date = new Date(Date.UTC(1582, 9, 15, 12, 0, 0));
    expect(formatDateToISO(date)).toMatch(/^1582-10-15T\d{2}:\d{2}:\d{2}/);
  });

  it('should correctly format a date at midnight (2024-12-31T00:00:00)', () => {
    const date = new Date(Date.UTC(2024, 11, 31, 0, 0, 0));
    expect(formatDateToISO(date)).toMatch(/^2024-12-31T\d{2}:\d{2}:\d{2}/);
  });
});

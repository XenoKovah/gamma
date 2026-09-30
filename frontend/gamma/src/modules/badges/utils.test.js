import { groupBadgesByCategory, UNCATEGORIZED_KEY } from './utils';

describe('groupBadgesByCategory', () => {
  it('returns an empty array when there are no badges', () => {
    expect(groupBadgesByCategory([], 'Uncategorized')).toEqual([]);
    expect(groupBadgesByCategory(undefined, 'Uncategorized')).toEqual([]);
  });

  it('groups by category, alphabetically, with Uncategorized last', () => {
    const badges = [
      { id: 1, title: 'V', category: 'Volunteering' },
      { id: 2, title: 'N', category: '' },
      { id: 3, title: 'L', category: 'Learning' },
      { id: 4, title: 'W', category: '   ' }, // whitespace-only -> uncategorized
    ];

    const groups = groupBadgesByCategory(badges, 'Uncategorized');

    expect(groups.map((g) => g.key)).toEqual(['Learning', 'Volunteering', UNCATEGORIZED_KEY]);
    expect(groups[groups.length - 1].label).toBe('Uncategorized');
    expect(groups[groups.length - 1].badges.map((b) => b.id)).toEqual([2, 4]);
  });

  it('preserves the incoming order of badges within a category', () => {
    const badges = [
      { id: 10, title: 'first', category: 'Learning' },
      { id: 11, title: 'second', category: 'Learning' },
    ];

    const [learning] = groupBadgesByCategory(badges, 'Uncategorized');

    expect(learning.badges.map((b) => b.id)).toEqual([10, 11]);
  });
});

describe('expiry date helpers', () => {
  it('endOfDayIso pins a date to the end of that UTC day and passes blanks through as null', () => {
    const { endOfDayIso } = jest.requireActual('./utils');
    expect(endOfDayIso('2031-09-29')).toBe('2031-09-29T23:59:59Z');
    expect(endOfDayIso('')).toBeNull();
  });

  it('formatExpiryDate shows the UTC date, or the never label when unset', () => {
    const { formatExpiryDate } = jest.requireActual('./utils');
    expect(formatExpiryDate('2031-09-29T23:59:59Z', 'Never')).toBe('2031-09-29');
    expect(formatExpiryDate(null, 'Never')).toBe('Never');
  });
});

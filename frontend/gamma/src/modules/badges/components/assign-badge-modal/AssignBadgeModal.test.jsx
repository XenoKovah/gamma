import { parseUserIds } from '.';

describe('parseUserIds', () => {
  it('splits on commas, semicolons, spaces and newlines', () => {
    expect(parseUserIds('jdoe, asmith; bwayne\nckent')).toEqual([
      'jdoe', 'asmith', 'bwayne', 'ckent',
    ]);
  });

  it('trims whitespace and ignores empty entries', () => {
    expect(parseUserIds('  jdoe ,, \n  ,asmith  ')).toEqual(['jdoe', 'asmith']);
  });

  it('de-duplicates while preserving first-seen order', () => {
    expect(parseUserIds('jdoe, asmith, jdoe')).toEqual(['jdoe', 'asmith']);
  });

  it('returns an empty array for blank input', () => {
    expect(parseUserIds('   \n  ')).toEqual([]);
  });
});

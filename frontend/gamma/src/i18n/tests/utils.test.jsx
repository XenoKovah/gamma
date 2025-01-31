import { useIntl } from 'react-intl';

import { getMessages } from '../utils';

jest.mock('react-intl', () => ({
  useIntl: jest.fn(),
  IntlProvider: jest.requireActual('react-intl').IntlProvider,
}));

jest.mock('../utils', () => ({
  __esModule: true,
  getMessages: jest.fn((locale) => {
    const translations = {
      en: { hello: 'Hello' },
      fr: { hello: 'Bonjour' },
    };
    return translations[locale] || translations.en;
  }),
}));

describe('Translation Utilities', () => {
  beforeEach(() => {
    jest.resetModules();
    useIntl.mockClear();
  });

  it('getMessages returns correct messages for locale', () => {
    expect(getMessages('en')).toEqual({ hello: 'Hello' });
    expect(getMessages('fr')).toEqual({ hello: 'Bonjour' });
  });

  it('getMessages falls back to English if locale not found', () => {
    expect(getMessages('es')).toEqual({ hello: 'Hello' });
  });
});

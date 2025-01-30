import React from 'react';
import { IntlProvider } from 'react-intl';
import { render } from '@testing-library/react';

import { getMessages } from './i18n/utils';

global.matchMedia = global.matchMedia || (() => ({
  matches: false,
  addListener() {},
  removeListener() {},
}));

export const renderWithProviders = (children) => {
  const messages = getMessages('en');

  return render(
    <IntlProvider locale="en" messages={messages}>
      {children}
    </IntlProvider>,
  );
};

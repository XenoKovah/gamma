import React from 'react';
import PropTypes from 'prop-types';
import { IntlProvider } from 'react-intl';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';

import { getMessages } from './i18n/utils';

global.matchMedia = global.matchMedia || (() => ({
  matches: false,
  addListener() {},
  removeListener() {},
}));

export const renderWithProviders = (ui) => {
  const messages = getMessages('en');
  const queryClient = new QueryClient();

  const Wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <IntlProvider locale="en" messages={messages}>
          {children}
        </IntlProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );

  Wrapper.propTypes = {
    children: PropTypes.node.isRequired,
  };

  return render(ui, { wrapper: Wrapper });
};

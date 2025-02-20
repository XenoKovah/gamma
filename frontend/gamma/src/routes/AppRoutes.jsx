import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { IntlProvider } from 'react-intl';
import { QueryClient, QueryClientProvider } from 'react-query';

import { getMessages } from '../i18n/utils';
import NotFound from '../modules/not-found';
import { getCookieByName } from '../utils';
import { allRoutes, allProviders } from './utils';
import { ROUTES } from '.';

const queryClient = new QueryClient();

const AppRoutes = () => {
  const locale = getCookieByName('openedx-language-preference') || 'en';
  const messages = getMessages(locale);

  // Wraps the application routes with all dynamically imported context providers.
  // Each provider from `allProviders` is applied in a nested manner.
  const WrappedProviders = allProviders.reduce(
    (children, Provider) => <Provider>{children}</Provider>,
    <Router basename={ROUTES.APP_BASE_NAME}>
      <Routes>
        {allRoutes.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>,
  );

  return (
    <QueryClientProvider client={queryClient}>
      <IntlProvider locale={locale} messages={messages}>
        {WrappedProviders}
      </IntlProvider>
    </QueryClientProvider>
  );
};

export default AppRoutes;

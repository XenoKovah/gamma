import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { IntlProvider } from 'react-intl';

import { getMessages } from '../i18n/utils';
import NotFound from '../modules/not-found';
import allRoutes from './expandRoutes';

const AppRoutes = () => {
  const locale = 'en';
  const messages = getMessages(locale);

  return (
    <IntlProvider locale={locale} messages={messages}>
      <Router basename="/gamma">
        <Routes>
          {allRoutes.map(({ path, element }) => (
            <Route key={path} path={path} element={element} />
          ))}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </IntlProvider>
  );
};

export default AppRoutes;

import React from 'react';
import { useIntl } from 'react-intl';
import { Spinner } from '@openedx/paragon';

import messages from '../../i18n';

const Loader = () => {
  const intl = useIntl();

  return (
    <div className="loader">
      <Spinner
        animation="border"
        screenReaderText={intl.formatMessage(messages.loaderScreenReaderText)}
      />
    </div>
  );
};

export default Loader;

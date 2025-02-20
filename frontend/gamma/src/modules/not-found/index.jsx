import React from 'react';
import { Container, Alert } from '@openedx/paragon';
import { Info as InfoIcon } from '@openedx/paragon/icons';
import { useIntl } from 'react-intl';

import messages from './i18n';

const NotFound = () => {
  const intl = useIntl();
  const notFoundAlertText = intl.formatMessage(messages.notFoundAlertText);

  return (
    <Container className="mt-4" size="lg">
      <Alert variant="danger" icon={InfoIcon}>
        <Alert.Heading>404</Alert.Heading>
        <p>{notFoundAlertText}</p>
      </Alert>
    </Container>
  );
};

export default NotFound;

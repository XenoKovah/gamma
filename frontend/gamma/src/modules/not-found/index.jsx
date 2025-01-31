import React from 'react';
import { Container, Alert } from '@openedx/paragon';
import { Info as InfoIcon } from '@openedx/paragon/icons';

import { useTranslate } from '../../i18n/utils';

const NotFound = () => {
  const notFoundAlertText = useTranslate('modules.not-found.alert.text');

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

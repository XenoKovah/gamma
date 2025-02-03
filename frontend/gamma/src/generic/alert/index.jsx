import React from 'react';
import PropTypes from 'prop-types';
import { Alert } from '@openedx/paragon';
import { Info as InfoIcon } from '@openedx/paragon/icons';

import { useTranslate } from '../../i18n/utils';

const AlertComponent = ({
  variant, title, description, onClose,
}) => (
  <Alert
    className="mb-4"
    variant={variant}
    icon={InfoIcon}
    dismissible
    closeLabel={useTranslate('generic.alert.button.close.title')}
    onClose={onClose}
  >
    <Alert.Heading>{title}</Alert.Heading>
    <p>{description}</p>
  </Alert>
);

AlertComponent.propTypes = {
  variant: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  onClose: PropTypes.func,
};

export default AlertComponent;

import React from 'react';
import PropTypes from 'prop-types';
import { AlertModal as ParagonAlertModal, ActionRow, Button } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';

const AlertModal = ({
  title, isOpen, onClose, onDelete, description,
}) => {
  const messages = {
    cancelButtonText: useTranslate('generic.modal.alert.button.cancel.text'),
    deleteButtonText: useTranslate('generic.modal.alert.button.delete.text'),
  };

  return (
    <ParagonAlertModal
      title={title}
      isOpen={isOpen}
      onClose={onClose}
      footerNode={(
        <ActionRow>
          <Button variant="tertiary" onClick={onClose}>
            {messages.cancelButtonText}
          </Button>
          <Button variant="danger" onClick={onDelete}>
            {messages.deleteButtonText}
          </Button>
        </ActionRow>
      )}
    >
      <p>{description}</p>
    </ParagonAlertModal>
  );
};

AlertModal.propTypes = {
  title: PropTypes.string.isRequired,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  description: PropTypes.string.isRequired,
};

export default AlertModal;

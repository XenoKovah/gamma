import React from 'react';
import PropTypes from 'prop-types';
import {
  AlertModal as ParagonAlertModal,
  ActionRow,
  Button,
} from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';
import { StatusButton, submitBtnStatuses } from '../status-button';

const AlertModal = ({
  title, isOpen, onClose, onDelete,
  description, isStatefulButton, submitStatus,
}) => {
  const messages = {
    cancelButtonText: useTranslate('generic.modal.alert.button.cancel.text'),
    deleteButtonText: useTranslate('generic.modal.alert.button.delete.text'),
    statefulButtonLabels: {
      default: useTranslate('generic.modal.alert.button.stateful.default.text'),
      pending: useTranslate('generic.modal.alert.button.stateful.pending.text'),
      complete: useTranslate('generic.modal.alert.button.stateful.complete.text'),
      error: useTranslate('generic.modal.alert.button.stateful.error.text'),
    },
  };

  const statefulButtonLabels = {
    default: messages.statefulButtonLabels.default,
    pending: messages.statefulButtonLabels.pending,
    complete: messages.statefulButtonLabels.complete,
    error: messages.statefulButtonLabels.error,
  };

  return (
    <ParagonAlertModal
      title={title}
      isOpen={isOpen}
      onClose={onClose}
      footerNode={(
        <ActionRow>
          <Button className="mx-2" variant="tertiary" onClick={onClose}>
            {messages.cancelButtonText}
          </Button>
          {isStatefulButton ? (
            <StatusButton
              variant="danger"
              labels={statefulButtonLabels}
              options={{
                submitStatus,
                submitFn: onDelete,
              }}
            />
          ) : (
            <Button variant="danger" onClick={onDelete}>
              {messages.deleteButtonText}
            </Button>
          )}
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
  isStatefulButton: PropTypes.bool,
  submitStatus: PropTypes.string,
};

AlertModal.defaultProps = {
  isStatefulButton: false,
  submitStatus: submitBtnStatuses.DEFAULT,
};

export default AlertModal;

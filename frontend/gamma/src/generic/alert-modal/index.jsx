import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import {
  AlertModal as ParagonAlertModal,
  ActionRow,
  Button,
} from '@openedx/paragon';

import messages from '../../i18n';
import { StatusButton, submitBtnStatuses } from '../status-button';

const AlertModal = ({
  title, isOpen, onClose, onDelete,
  description, isStatefulButton, submitStatus,
}) => {
  const intl = useIntl();

  const statefulButtonLabels = {
    default: intl.formatMessage(messages.btnStatefulDefaultText),
    pending: intl.formatMessage(messages.btnStatefulPendingText),
    complete: intl.formatMessage(messages.btnStatefulCompleteText),
    error: intl.formatMessage(messages.btnStatefulErrorText),
  };

  return (
    <ParagonAlertModal
      title={title}
      isOpen={isOpen}
      onClose={onClose}
      footerNode={(
        <ActionRow>
          <Button className="mx-2" variant="tertiary" onClick={onClose}>
            {intl.formatMessage(messages.alertBtnCancelText)}
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
              {intl.formatMessage(messages.alertBtnDeleteText)}
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

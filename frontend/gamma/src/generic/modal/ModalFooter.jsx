import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Button, ModalDialog } from '@openedx/paragon';

import messages from '../../i18n';
import { StatusButton, submitBtnStatuses } from '../status-button';

const ModalFooter = ({
  closeBtnTitle, submitBtnOptions, handleClose,
}) => {
  const intl = useIntl();

  const statefulButtonLabels = {
    default: intl.formatMessage(messages.modalDialogBtnStatefulDefaultText),
    pending: intl.formatMessage(messages.modalDialogBtnStatefulPendingText),
    complete: intl.formatMessage(messages.modalDialogBtnStatefulCompleteText),
    error: intl.formatMessage(messages.modalDialogBtnStatefulErrorText),
  };

  const resolvedSubmitBtnTitle = submitBtnOptions.title || intl.formatMessage(messages.modalDialogBtnSubmitText);
  const statefulButtonVariant = submitBtnOptions.submitStatus === submitBtnStatuses.ERROR.toLocaleLowerCase()
    ? 'danger' : 'primary';

  return (
    <ModalDialog.Footer>
      <Button variant="tertiary" onClick={handleClose} className="mx-2">
        {closeBtnTitle}
      </Button>
      {submitBtnOptions.isStatefulButton ? (
        <StatusButton
          options={{
            submitStatus: submitBtnOptions.submitStatus,
            submitFn: submitBtnOptions.submitFn,
            disabled: submitBtnOptions.disabled,
          }}
          variant={statefulButtonVariant}
          labels={statefulButtonLabels}
        />
      ) : (
        <Button
          disabled={submitBtnOptions?.disabled}
          onClick={submitBtnOptions?.submitFn}
        >
          {resolvedSubmitBtnTitle}
        </Button>
      )}
    </ModalDialog.Footer>
  );
};

ModalFooter.propTypes = {
  closeBtnTitle: PropTypes.string,
  submitBtnOptions: PropTypes.shape({
    show: PropTypes.bool,
    title: PropTypes.string,
    submitFn: PropTypes.func,
    disabled: PropTypes.bool,
    isStatefulButton: PropTypes.bool,
    submitStatus: PropTypes.string,
  }),
  handleClose: PropTypes.func.isRequired,
};

ModalFooter.defaultProps = {
  closeBtnTitle: undefined,
  submitBtnOptions: {
    show: false,
    title: undefined,
    submitFn: undefined,
    disabled: false,
    isStatefulButton: false,
    submitStatus: submitBtnStatuses.DEFAULT,
  },
};

export default ModalFooter;

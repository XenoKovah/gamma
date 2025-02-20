import React from 'react';
import PropTypes from 'prop-types';
import { Button, ModalDialog } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';
import { StatusButton, submitBtnStatuses } from '../status-button';

const ModalFooter = ({
  closeBtnTitle, submitBtnOptions, handleClose,
}) => {
  const messages = {
    submitButtonText: useTranslate('generic.modal.dialog.button.submit.text'),
    statefulButtonLabels: {
      default: useTranslate('generic.modal.dialog.button.stateful.default.text'),
      pending: useTranslate('generic.modal.dialog.button.stateful.pending.text'),
      complete: useTranslate('generic.modal.dialog.button.stateful.complete.text'),
      error: useTranslate('generic.modal.dialog.button.stateful.error.text'),
    },
  };

  const statefulButtonLabels = {
    default: messages.statefulButtonLabels.default,
    pending: messages.statefulButtonLabels.pending,
    complete: messages.statefulButtonLabels.complete,
    error: messages.statefulButtonLabels.error,
  };

  const resolvedSubmitBtnTitle = submitBtnOptions.title || messages.submitButtonText;
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

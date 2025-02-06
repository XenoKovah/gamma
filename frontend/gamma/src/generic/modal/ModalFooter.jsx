import React from 'react';
import PropTypes from 'prop-types';
import { Button, ModalDialog } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';

const ModalFooter = ({
  closeBtnTitle, submitBtnOptions, handleClose,
}) => {
  const messages = {
    submitButtonText: useTranslate('generic.modal.dialog.button.submit.text'),
  };
  const resolvedSubmitBtnTitle = submitBtnOptions.title || messages.submitButtonText;

  return (
    <ModalDialog.Footer>
      <Button variant="tertiary" onClick={handleClose}>
        {closeBtnTitle}
      </Button>
      <Button
        className="ml-2"
        disabled={submitBtnOptions?.disabled}
        onClick={submitBtnOptions?.submitFn}
      >
        {resolvedSubmitBtnTitle}
      </Button>
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
  },
};

export default ModalFooter;

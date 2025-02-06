import React from 'react';
import PropTypes from 'prop-types';
import { ModalDialog } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';
import { MODAL_SIZES, ZINDEX_MODAL } from './constants';
import ModalFooter from './ModalFooter';

const Modal = ({
  size,
  title,
  isOpen,
  variant,
  children,
  isBlocking,
  closeLabel,
  handleClose,
  closeBtnTitle,
  hasCloseButton,
  submitBtnOptions,
  isOverflowVisible,
  isFullscreenScroll,
  isFullscreenOnMobile,
}) => {
  const messages = {
    cancelButtonText: useTranslate('generic.modal.dialog.button.cancel.text'),
  };
  const resolvedCloseBtnTitle = closeBtnTitle || messages.cancelButtonText;

  return (
    <ModalDialog
      title={title}
      isOpen={isOpen}
      onClose={handleClose}
      hasCloseButton={hasCloseButton}
      className="gamification-modal-dialog"
      closeLabel={closeLabel}
      isBlocking={isBlocking}
      isFullscreenOnMobile={isFullscreenOnMobile}
      isFullscreenScroll={isFullscreenScroll}
      isOverflowVisible={isOverflowVisible}
      size={size}
      variant={variant}
      zIndex={ZINDEX_MODAL}
    >
      <ModalDialog.Header>
        <ModalDialog.Title>{title}</ModalDialog.Title>
      </ModalDialog.Header>
      <ModalDialog.Body>{children}</ModalDialog.Body>
      <ModalFooter
        closeBtnTitle={resolvedCloseBtnTitle}
        submitBtnOptions={submitBtnOptions}
        handleClose={handleClose}
      />
    </ModalDialog>
  );
};

Modal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  size: PropTypes.oneOf(MODAL_SIZES),
  hasCloseButton: PropTypes.bool,
  closeBtnTitle: PropTypes.string,
  submitBtnOptions: PropTypes.shape({
    title: PropTypes.string,
    submitFn: PropTypes.func,
    disabled: PropTypes.bool,
  }),
  isBlocking: PropTypes.bool,
  variant: PropTypes.string,
  closeLabel: PropTypes.string,
  isOverflowVisible: PropTypes.bool,
  isFullscreenScroll: PropTypes.bool,
  isFullscreenOnMobile: PropTypes.bool,
};

Modal.defaultProps = {
  size: 'md',
  hasCloseButton: true,
  closeBtnTitle: undefined,
  submitBtnOptions: {
    title: undefined,
    submitFn: undefined,
    disabled: false,
  },
  isBlocking: false,
  isFullscreenOnMobile: false,
  isFullscreenScroll: false,
  variant: 'default',
  closeLabel: '',
  isOverflowVisible: false,
};

export default Modal;

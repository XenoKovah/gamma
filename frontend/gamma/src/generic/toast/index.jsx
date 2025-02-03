import React from 'react';
import PropTypes from 'prop-types';
import { Toast } from '@openedx/paragon';

const ToastComponent = ({
  text, variant, isShow, onClose,
}) => (
  <Toast
    show={isShow}
    className={`toast-component toast-${variant || ''}`}
    variant={variant}
    onClose={onClose}
  >
    {text}
  </Toast>
);

ToastComponent.propTypes = {
  text: PropTypes.string.isRequired,
  variant: PropTypes.oneOf(['danger']),
  isShow: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ToastComponent;

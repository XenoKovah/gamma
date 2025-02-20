import React from 'react';
import PropTypes from 'prop-types';
import { Toast } from '@openedx/paragon';

const DEFAULT_DELAY = 5000;

const ToastComponent = ({
  text, variant, isShow, onClose, delay,
}) => (
  <Toast
    show={isShow}
    className={`toast-component toast-${variant || ''}`}
    variant={variant}
    onClose={onClose}
    delay={delay}
  >
    {text}
  </Toast>
);

ToastComponent.propTypes = {
  text: PropTypes.string.isRequired,
  variant: PropTypes.oneOf(['danger']),
  isShow: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  delay: PropTypes.number,
};

ToastComponent.defaultProps = {
  variant: 'danger',
  delay: DEFAULT_DELAY,
};

export default ToastComponent;

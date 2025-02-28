import React from 'react';
import PropTypes from 'prop-types';
import { Toast } from '@openedx/paragon';
import classNames from 'classnames';

export const DEFAULT_DELAY = 5000;
export const TOAST_VARIANTS = ['danger', 'success'];

const ToastComponent = ({
  text, variant, isShow, onClose, delay, className,
}) => (
  <Toast
    show={isShow}
    className={classNames(
      'toast-component',
      { [`toast-${variant}`]: variant },
      className,
    )}
    variant={variant}
    onClose={onClose}
    delay={delay}
  >
    {text}
  </Toast>
);

ToastComponent.propTypes = {
  text: PropTypes.string.isRequired,
  variant: PropTypes.oneOf(TOAST_VARIANTS),
  isShow: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  delay: PropTypes.number,
  className: PropTypes.string,
};

ToastComponent.defaultProps = {
  variant: TOAST_VARIANTS[0],
  delay: DEFAULT_DELAY,
  className: '',
};

export default ToastComponent;

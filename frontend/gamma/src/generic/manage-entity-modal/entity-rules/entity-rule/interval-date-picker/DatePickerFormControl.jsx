import React, { forwardRef } from 'react';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';

const DatePickerFormControl = forwardRef(
  ({
    value, onClick, className, placeholder, onBlur,
  }, ref) => {
    const handleKyDown = (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onClick?.(event);
      }
    };

    return (
      <Form.Control
        ref={ref}
        className={className}
        floatingLabel={placeholder}
        value={value}
        onClick={onClick}
        onBlur={onBlur}
        onKeyDown={handleKyDown}
        tabIndex={0}
      />
    );
  },
);

DatePickerFormControl.propTypes = {
  value: PropTypes.string,
  onClick: PropTypes.func,
  className: PropTypes.string,
  placeholder: PropTypes.string,
  onBlur: PropTypes.func,
};

DatePickerFormControl.defaultProps = {
  value: '',
  onClick: undefined,
  className: '',
  placeholder: '',
  onBlur: undefined,
};

export default DatePickerFormControl;

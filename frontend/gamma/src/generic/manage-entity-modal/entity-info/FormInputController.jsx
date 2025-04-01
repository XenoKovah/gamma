import React from 'react';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import {
  Col, Form, breakpoints, useMediaQuery,
} from '@openedx/paragon';

const FormInputController = ({
  label, name, type, as, hasCol, autoResize,
}) => {
  const {
    values, errors, touched, handleChange, handleBlur, setFieldValue,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const handleTrimmedBlur = (e) => {
    const { name: fieldName, value } = e.target;
    const trimmedValue = value.trim();

    if (value !== trimmedValue) {
      setFieldValue(fieldName, trimmedValue);
    }

    handleBlur(e);
  };

  const InputComponent = (
    <>
      <Form.Control
        floatingLabel={label}
        name={name}
        as={as}
        type={type}
        value={values[name]}
        onChange={handleChange}
        onBlur={handleTrimmedBlur}
        isInvalid={touched[name] && !!errors[name]}
        autoResize={autoResize}
      />
      {touched[name] && errors[name] && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {errors[name]}
        </Form.Control.Feedback>
      )}
    </>
  );

  return hasCol ? (
    <Form.Group as={Col} controlId={`formEntity${name}`} size={isExtraSmall ? null : 'sm'}>
      {InputComponent}
    </Form.Group>
  ) : (
    <Form.Group controlId={`formEntity${name}`} size={isExtraSmall ? null : 'sm'}>
      {InputComponent}
    </Form.Group>
  );
};

FormInputController.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  type: PropTypes.string,
  as: PropTypes.string,
  hasCol: PropTypes.bool,
  autoResize: PropTypes.bool,
};

FormInputController.defaultProps = {
  type: 'text',
  as: 'input',
  hasCol: true,
  autoResize: false,
};

export default FormInputController;

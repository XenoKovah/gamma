import React from 'react';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import {
  Col, Form, breakpoints, useMediaQuery,
} from '@openedx/paragon';

const FormInputController = ({
  label, name, type, as, hasCol,
}) => {
  const {
    values, errors, touched, handleChange, handleBlur,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const InputComponent = (
    <>
      <Form.Control
        floatingLabel={label}
        name={name}
        as={as}
        type={type}
        value={values[name]}
        onChange={handleChange}
        onBlur={handleBlur}
        isInvalid={touched[name] && !!errors[name]}
      />
      {touched[name] && errors[name] && (
        <Form.Control.Feedback className="badge-modal-feedback" type="invalid">
          {errors[name]}
        </Form.Control.Feedback>
      )}
    </>
  );

  return hasCol ? (
    <Form.Group as={Col} controlId={`formBadge${name}`} size={isExtraSmall ? null : 'sm'}>
      {InputComponent}
    </Form.Group>
  ) : (
    <Form.Group controlId={`formBadge${name}`} size={isExtraSmall ? null : 'sm'}>
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
};

FormInputController.defaultProps = {
  type: 'text',
  as: 'input',
  hasCol: true,
};

export default FormInputController;

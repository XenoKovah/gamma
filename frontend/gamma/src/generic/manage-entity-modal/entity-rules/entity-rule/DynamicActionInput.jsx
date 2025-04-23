import React from 'react';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';
import { useFormikContext } from 'formik';

const DynamicActionInput = ({ ruleIndex, data }) => {
  const {
    values, touched, handleBlur, errors, setFieldValue,
  } = useFormikContext();

  if (!values.rules?.[ruleIndex]?.action?.eventType) {
    return null;
  }

  const selectedAction = data.actions.find(
    action => action.eventName === values.rules[ruleIndex].action.eventType,
  );
  const schemaField = selectedAction?.schema?.[0];

  if (!schemaField) {
    return null;
  }

  const fieldName = schemaField.field;
  const fieldTitle = schemaField.title;
  const isActionFieldTouched = touched.rules?.[ruleIndex]?.action?.[fieldName];

  return (
    <Form.Group controlId={`rules.${ruleIndex}.action.${fieldName}`} size="sm">
      <Form.Control
        type="number"
        className="mr-0"
        floatingLabel={fieldTitle}
        name={`rules.${ruleIndex}.action.${fieldName}`}
        value={values.rules?.[ruleIndex]?.action?.[fieldName] ?? ''}
        onChange={(e) => {
          setFieldValue(`rules.${ruleIndex}.action.${fieldName}`, e.target.value);
        }}
        onBlur={handleBlur}
        isInvalid={isActionFieldTouched && !!errors.rules?.[ruleIndex]?.action}
      />
      {isActionFieldTouched && errors.rules?.[ruleIndex]?.action && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {errors.rules?.[ruleIndex]?.action}
        </Form.Control.Feedback>
      )}
    </Form.Group>
  );
};

DynamicActionInput.propTypes = {
  ruleIndex: PropTypes.number.isRequired,
  data: PropTypes.shape({
    actions: PropTypes.arrayOf(PropTypes.shape({
      eventName: PropTypes.string.isRequired,
      schema: PropTypes.arrayOf(PropTypes.shape({
        field: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
      })),
    })).isRequired,
  }).isRequired,
};

export default DynamicActionInput;

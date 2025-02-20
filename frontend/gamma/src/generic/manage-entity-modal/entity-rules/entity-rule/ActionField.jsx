import React from 'react';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';

import { useTranslate } from '../../../../i18n/utils';

const ActionField = ({
  name,
  type,
  label,
  options,
  errors,
  values,
  touched,
  ruleIndex,
  handleBlur,
  setFieldValue,
}) => {
  const fieldName = `rules.${ruleIndex}.action.${name}`;
  const fieldValue = values.rules?.[ruleIndex]?.action?.[name] ?? '';

  const messages = {
    eventTypeLabel: useTranslate('generic.modal.entity.action.event.name.label', { eventType: label.toLowerCase() }),
  };

  const hasError = touched.rules?.[ruleIndex]?.action?.[name] && !!errors.rules?.[ruleIndex]?.action?.[name];

  return (
    <Form.Group controlId={fieldName} size="sm">
      <Form.Control
        as={type === 'select' ? 'select' : 'input'}
        type={type === 'number' ? 'number' : 'text'}
        className="mr-0"
        floatingLabel={label}
        name={fieldName}
        value={fieldValue}
        onChange={(e) => setFieldValue(fieldName, e.target.value)}
        onBlur={handleBlur}
        isInvalid={hasError}
      >
        {type === 'select' ? (
          <>
            <option value="">{messages.eventTypeLabel}</option>
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </>
        ) : null}
      </Form.Control>
      {hasError && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {errors.rules?.[ruleIndex]?.action?.[name]}
        </Form.Control.Feedback>
      )}
    </Form.Group>
  );
};

ActionField.propTypes = {
  ruleIndex: PropTypes.number.isRequired,
  name: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['text', 'number', 'select']).isRequired,
  values: PropTypes.shape({
    rules: PropTypes.arrayOf(
      PropTypes.shape({
        action: PropTypes.objectOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])),
      }),
    ),
  }).isRequired,
  touched: PropTypes.shape({
    rules: PropTypes.arrayOf(
      PropTypes.shape({
        action: PropTypes.objectOf(PropTypes.bool),
      }),
    ),
  }).isRequired,
  errors: PropTypes.shape({
    rules: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(
        PropTypes.shape({
          action: PropTypes.objectOf(PropTypes.string),
        }),
      ),
    ]),
  }).isRequired,
  setFieldValue: PropTypes.func.isRequired,
  handleBlur: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.string),
};

export default ActionField;

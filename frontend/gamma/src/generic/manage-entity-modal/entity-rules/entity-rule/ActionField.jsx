import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';

import messages from '../../../../i18n';

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
  const intl = useIntl();
  const fieldName = `rules.${ruleIndex}.action.${name}`;
  const fieldValue = values.rules?.[ruleIndex]?.action?.[name] ?? '';
  const optionsMap = new Map(options.map(option => [option.eventName, option.id]));

  const hasError = touched.rules?.[ruleIndex]?.action?.[name] && !!errors.rules?.[ruleIndex]?.action?.[name];

  const handleChange = (e) => {
    const selectedValue = e.target.value;
    const selectedId = optionsMap.get(selectedValue) || '';

    setFieldValue(fieldName, selectedValue);

    if (selectedId) {
      setFieldValue(`rules.${ruleIndex}.action.id`, selectedId);
    }
  };

  return (
    <Form.Group controlId={fieldName} size="sm">
      <Form.Control
        as={type === 'select' ? 'select' : 'input'}
        type={type === 'number' ? 'number' : 'text'}
        className="mr-0"
        floatingLabel={label}
        name={fieldName}
        value={fieldValue}
        onChange={handleChange}
        onBlur={handleBlur}
        isInvalid={hasError}
      >
        {type === 'select' ? (
          <>
            <option value="">
              {intl.formatMessage(
                messages.modalEntityActionEventNameLabelText,
                { eventType: label.toLowerCase() },
              )}
            </option>
            {options.map((option) => (
              <option key={option.id} value={option.eventName}>
                {option.title}
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
    rules: PropTypes.oneOfType([
      PropTypes.arrayOf(
        PropTypes.shape({
          action: PropTypes.objectOf(PropTypes.bool),
        }),
      ),
      PropTypes.object,
    ]),
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
  options: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      eventName: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

export default ActionField;

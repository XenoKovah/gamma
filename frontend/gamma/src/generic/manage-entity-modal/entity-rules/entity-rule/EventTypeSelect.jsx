import React from 'react';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';
import { useFormikContext } from 'formik';
import { useIntl } from 'react-intl';

import messages from '../../../../i18n';

// Actions that may be used in more than one rule of the same entity. This lets an admin
// build a badge that requires completing several specific courses — one "Get a Course
// Certificate" rule per course, each scoped by its own course filter. The backend
// (CommonEventProcessor) advances a rule's progress only for events matching that rule's
// filters, so multiple certificate rules behave as an AND across courses.
export const REPEATABLE_EVENT_NAMES = ['edx_certificate_created'];

const EventTypeSelect = ({ ruleIndex, translations, data }) => {
  const intl = useIntl();
  const {
    values, touched, handleBlur, errors, setFieldValue,
  } = useFormikContext();

  const selectedEventType = values.rules?.[ruleIndex]?.action?.eventType ?? '';
  const existingEventTypes = values.rules
    ?.map((rule, idx) => idx !== ruleIndex && rule.action?.eventType)
    .filter(Boolean);

  // Filter out actions already used by other rules, except repeatable ones (e.g. course
  // certificates), which may scope to a different course in each rule.
  const filteredActions = data.actions.filter(
    action => REPEATABLE_EVENT_NAMES.includes(action.eventName)
      || !existingEventTypes.includes(action.eventName)
      || action.eventName === selectedEventType,
  );

  const isEventTypesFieldTouched = touched.rules?.[ruleIndex]?.action?.eventType;
  const eventTypesFieldError = errors.rules?.[ruleIndex]?.action?.eventType;

  const handleChange = (e) => {
    const selectedValue = e.target.value;
    const selectedAction = data.actions.find(action => action.eventName === selectedValue);
    const selectedId = selectedAction?.id || '';

    setFieldValue(`rules.${ruleIndex}.action.eventType`, selectedValue);
    if (selectedId) {
      setFieldValue(`rules.${ruleIndex}.action.id`, selectedId);
      // Reset count/points when action changes
      setFieldValue(`rules.${ruleIndex}.action.count`, '');
      setFieldValue(`rules.${ruleIndex}.action.points`, '');
    }
  };

  return (
    <Form.Group controlId={`rules.${ruleIndex}.action.eventType`} size="sm">
      <Form.Control
        as="select"
        className="mr-0"
        data-testid="event-type-select"
        name={`rules.${ruleIndex}.action.eventType`}
        value={selectedEventType}
        onChange={handleChange}
        onBlur={handleBlur}
        isInvalid={isEventTypesFieldTouched && !!eventTypesFieldError}
      >
        <option value="">
          {intl.formatMessage(
            messages.modalEntityActionEventNameLabelText,
            { eventType: translations.action.toLowerCase() },
          )}
        </option>
        {filteredActions.map((action) => (
          <option key={action.id} value={action.eventName}>
            {action.title}
          </option>
        ))}
      </Form.Control>
      {isEventTypesFieldTouched && eventTypesFieldError && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {eventTypesFieldError}
        </Form.Control.Feedback>
      )}
    </Form.Group>
  );
};

EventTypeSelect.propTypes = {
  ruleIndex: PropTypes.number.isRequired,
  translations: PropTypes.shape({
    action: PropTypes.string.isRequired,
  }).isRequired,
  data: PropTypes.shape({
    actions: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string.isRequired,
      eventName: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
    })).isRequired,
  }).isRequired,
};

export default EventTypeSelect;

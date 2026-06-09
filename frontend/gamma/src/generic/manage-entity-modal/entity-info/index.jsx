import React from 'react';
import { useIntl } from 'react-intl';
import classNames from 'classnames';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';
import { useFormikContext } from 'formik';

import messages from '../../../i18n';
import FormInputController from './FormInputController';

const EntityInfo = () => {
  const intl = useIntl();
  const {
    values, initialValues, errors, touched, handleChange, handleBlur, setFieldValue,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const handleCheckboxChange = (event) => {
    handleChange({ target: { name: 'isActive', value: event.target.checked } });
  };

  const handlePointsChange = (event) => {
    const { value } = event.target;
    // Keep points as a number in form state (an empty input means 0 points).
    setFieldValue('points', value === '' ? 0 : Number(value));
  };

  return (
    <div className="manage-entity-modal-information mb-4">
      <h3 className="h4 mb-3">{intl.formatMessage(messages.modalEntityInfoHeadingText)}</h3>
      <Form.Row className={classNames({ 'flex-column': isExtraSmall })}>
        <FormInputController
          label={intl.formatMessage(messages.modalEntityInfoLabelEntityTitle)}
          name="title"
        />
        {Object.hasOwn(initialValues, 'slug') && (
          <FormInputController
            label={intl.formatMessage(messages.modalEntityInfoLabelEntitySlugText)}
            name="slug"
          />
        )}
      </Form.Row>
      <FormInputController
        label={intl.formatMessage(messages.modalEntityInfoLabelEntityDescriptionText)}
        name="description"
        as="textarea"
        autoResize
        hasCol={false}
      />
      {Object.hasOwn(initialValues, 'manualCriteria') && (
        <FormInputController
          label={intl.formatMessage(messages.modalEntityInfoLabelEntityManualCriteriaText)}
          name="manualCriteria"
          as="textarea"
          autoResize
          hasCol={false}
        />
      )}
      {Object.hasOwn(initialValues, 'points') && (
        <Form.Group controlId="formEntityPoints" size="sm">
          <Form.Control
            type="number"
            min={0}
            step={1}
            className="mr-0"
            floatingLabel={intl.formatMessage(messages.modalEntityInfoLabelEntityPointsText)}
            name="points"
            value={values.points ?? 0}
            onChange={handlePointsChange}
            onBlur={handleBlur}
            isInvalid={touched.points && !!errors.points}
          />
          {touched.points && errors.points && (
            <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
              {errors.points}
            </Form.Control.Feedback>
          )}
        </Form.Group>
      )}
      {Object.hasOwn(initialValues, 'isActive') && (
        <Form.Group className="mb-4" controlId="formEntityActive">
          <Form.Checkbox
            className="manage-entity-modal-information-is-active"
            checked={values.isActive}
            onChange={handleCheckboxChange}
          >
            {intl.formatMessage(messages.modalEntityInfoLabelEntityIsActiveText)}
          </Form.Checkbox>
        </Form.Group>
      )}
    </div>
  );
};

export default EntityInfo;

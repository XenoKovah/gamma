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
    // Keep the raw input string in form state while editing so a negative entry
    // (the intermediate "-") and an empty field are preserved -- coercing to a number
    // here would clobber the "-". The value is normalised to a number on blur.
    setFieldValue('points', event.target.value);
  };

  const handlePointsBlur = (event) => {
    const number = Number(event.target.value);
    setFieldValue('points', event.target.value === '' || Number.isNaN(number) ? 0 : number);
    handleBlur(event);
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
      {Object.hasOwn(initialValues, 'category') && (
        <FormInputController
          label={intl.formatMessage(messages.modalEntityInfoLabelEntityCategoryText)}
          name="category"
          hasCol={false}
        />
      )}
      {Object.hasOwn(initialValues, 'points') && (
        <Form.Group controlId="formEntityPoints" size="sm">
          <Form.Control
            type="number"
            step={1}
            className="mr-0"
            floatingLabel={intl.formatMessage(messages.modalEntityInfoLabelEntityPointsText)}
            name="points"
            value={values.points ?? ''}
            onChange={handlePointsChange}
            onBlur={handlePointsBlur}
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

import React from 'react';
import { useIntl } from 'react-intl';
import classNames from 'classnames';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';
import { useFormikContext } from 'formik';

import messages from '../../../i18n';
import FormInputController from './FormInputController';

const EntityInfo = () => {
  const intl = useIntl();
  const { handleChange } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const handleCheckboxChange = (event) => {
    handleChange({ target: { name: 'isActive', value: event.target.checked } });
  };

  return (
    <div className="manage-entity-modal-information mb-4">
      <h2 className="h3 mb-3">{intl.formatMessage(messages.modalEntityInfoHeadingText)}</h2>
      <Form.Row className={classNames({ 'flex-column': isExtraSmall })}>
        <FormInputController
          label={intl.formatMessage(messages.modalEntityInfoLabelEntityTitle)}
          name="title"
        />
        <FormInputController
          label={intl.formatMessage(messages.modalEntityInfoLabelEntitySlugText)}
          name="slug"
        />
      </Form.Row>
      <FormInputController
        label={intl.formatMessage(messages.modalEntityInfoLabelEntityDescriptionText)}
        name="description"
        as="textarea"
        autoResize
        hasCol={false}
      />
      <Form.Group className="mb-4" controlId="formEntityActive">
        <Form.Checkbox
          className="manage-entity-modal-information-is-active"
          onChange={handleCheckboxChange}
        >
          {intl.formatMessage(messages.modalEntityInfoLabelEntityIsActiveText)}
        </Form.Checkbox>
      </Form.Group>
    </div>
  );
};

export default EntityInfo;

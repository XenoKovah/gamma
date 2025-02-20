import React from 'react';
import classNames from 'classnames';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';
import { useFormikContext } from 'formik';

import { useTranslate } from '../../../i18n/utils';
import FormInputController from './FormInputController';

const EntityInfo = () => {
  const { handleChange } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const messages = {
    heading: useTranslate('generic.modal.entity.information.heading'),
    entity: {
      titleLabel: useTranslate('generic.modal.entity.information.label.entity.title'),
      slugLabel: useTranslate('generic.modal.entity.information.label.entity.slug'),
      descriptionLabel: useTranslate('generic.modal.entity.information.label.entity.description'),
      isActive: useTranslate('generic.modal.entity.is-active.text'),
    },
  };

  const handleCheckboxChange = (event) => {
    handleChange({ target: { name: 'isActive', value: event.target.checked } });
  };

  return (
    <div className="manage-entity-modal-information mb-4">
      <h2 className="h3 mb-3">{messages.heading}</h2>
      <Form.Row className={classNames({ 'flex-column': isExtraSmall })}>
        <FormInputController label={messages.entity.titleLabel} name="title" />
        <FormInputController label={messages.entity.slugLabel} name="slug" />
      </Form.Row>
      <FormInputController
        label={messages.entity.descriptionLabel}
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
          {messages.entity.isActive}
        </Form.Checkbox>
      </Form.Group>
    </div>
  );
};

export default EntityInfo;

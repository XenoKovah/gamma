import React from 'react';
import classNames from 'classnames';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';
import { useFormikContext } from 'formik';

import { useTranslate } from '../../../../../i18n/utils';
import FormInputController from './FormInputController';

const BadgeInformation = () => {
  const { handleChange } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });
  const messages = {
    heading: useTranslate('modules.badges.modal.badge.information.heading'),
    badge: {
      titleLabel: useTranslate('modules.badges.modal.badge.information.label.badge.title'),
      slugLabel: useTranslate('modules.badges.modal.badge.information.label.badge.slug'),
      descriptionLabel: useTranslate('modules.badges.modal.badge.information.label.badge.description'),
      isActive: useTranslate('modules.badges.modal.badge.is-active.text'),
    },
  };

  return (
    <div className="badge-modal-information mb-4">
      <h2 className="h3 mb-3">{messages.heading}</h2>
      <Form.Row className={classNames({ 'flex-column': isExtraSmall })}>
        <FormInputController label={messages.badge.titleLabel} name="title" />
        <FormInputController label={messages.badge.slugLabel} name="slug" />
      </Form.Row>
      <FormInputController label={messages.badge.descriptionLabel} name="description" as="textarea" hasCol={false} />
      <Form.Group className="mb-4" controlId="formBadgeActive">
        <Form.Checkbox className="badge-modal-active" name="isActive" onChange={handleChange}>
          {messages.badge.isActive}
        </Form.Checkbox>
      </Form.Group>
    </div>
  );
};

export default BadgeInformation;

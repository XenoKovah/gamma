import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Form, Button, Figure, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import { useFormikContext } from 'formik';

import { useTranslate } from '../../../../../i18n/utils';

const BadgeImage = ({ imagePreview, handleImageUpload }) => {
  const { errors } = useFormikContext();
  const [isValidationTriggered, setIsValidationTriggered] = useState(false);
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const messages = {
    heading: useTranslate('modules.badges.modal.badge.image.heading'),
    uploadBtnTitle: useTranslate('modules.badges.modal.badge.image.button.upload'),
    badgePreviewScreenReaderText: useTranslate('modules.badges.modal.badge.image.preview.screenReader.text'),
    badgePreviewCaptionText: useTranslate('modules.badges.modal.badge.image.preview.caption'),
    imageRequiredText: useTranslate('modules.badges.modal.validation.image.required'),
    imageSize: useTranslate('modules.badges.modal.validation.image.size'),
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      setIsValidationTriggered(false);
    }

    handleImageUpload(event);
  };

  const handleUploadImageClick = () => {
    requestAnimationFrame(() => {
      setIsValidationTriggered(true);
    });
  };

  return (
    <div className="badge-modal-image mb-4">
      <h2 className="h3 mb-3">{messages.heading}</h2>
      <Form.Group className="mb-4" controlId="formBadgeImage" size={isExtraSmall ? null : 'sm'}>
        <Form.Control
          id="badge-image-upload"
          type="file"
          accept="image/png, image/jpeg, image/gif, image/webp"
          className="d-none"
          onChange={handleFileChange}
        />
        <Form.Label className="m-0" htmlFor="badge-image-upload">
          <Button
            size={isExtraSmall ? 'md' : 'sm'}
            as="span"
            role="button"
            onClick={handleUploadImageClick}
          >
            {messages.uploadBtnTitle}
          </Button>
        </Form.Label>

        {errors.image === messages.imageSize && (
          <Form.Control.Feedback type="invalid" className="badge-modal-feedback">
            {errors.image}
          </Form.Control.Feedback>
        )}

        {isValidationTriggered && !imagePreview && (
          <Form.Control.Feedback type="invalid" className="badge-modal-feedback mt-1">
            {messages.imageRequiredText}
          </Form.Control.Feedback>
        )}

        {imagePreview && (
          <Figure className="mt-3 mb-0 d-block">
            <Figure.Caption className="small">
              {messages.badgePreviewCaptionText}
            </Figure.Caption>
            <Figure.Image
              className="badge-image-preview mb-0"
              alt={messages.badgePreviewScreenReaderText}
              src={imagePreview}
            />
          </Figure>
        )}
      </Form.Group>
    </div>
  );
};

BadgeImage.propTypes = {
  imagePreview: PropTypes.string,
  handleImageUpload: PropTypes.func.isRequired,
};

export default BadgeImage;

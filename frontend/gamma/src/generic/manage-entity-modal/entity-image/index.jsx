import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import {
  Form, Button, Figure, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import { useFormikContext } from 'formik';

import { useTranslate } from '../../../i18n/utils';

const EntityImage = ({ imagePreview, handleImageUpload }) => {
  const { errors } = useFormikContext();
  const [isValidationTriggered, setIsValidationTriggered] = useState(false);
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const fileInputRef = useRef(null);

  const messages = {
    heading: useTranslate('generic.modal.entity.image.heading'),
    uploadBtnTitle: useTranslate('generic.modal.entity.image.button.upload'),
    entityPreviewScreenReaderText: useTranslate('generic.modal.entity.image.preview.screenReader.text'),
    imageRequiredText: useTranslate('generic.modal.entity.validation.image.required'),
    imageSize: useTranslate('generic.modal.entity.validation.image.size'),
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

  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
      handleUploadImageClick();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      openFileDialog();
    }
  };

  return (
    <div className="manage-entity-modal-image mb-4">
      <h2 className="h3 mb-3">{messages.heading}</h2>
      <Form.Group className="mb-4" controlId="formEntityImage" size={isExtraSmall ? null : 'sm'}>
        <Form.Control
          ref={fileInputRef}
          id="entity-image-upload"
          type="file"
          accept="image/png, image/jpeg, image/gif, image/webp"
          className="d-none"
          onChange={handleFileChange}
        />
        <Form.Label className="m-0">
          <Button
            size={isExtraSmall ? 'md' : 'sm'}
            as="span"
            role="button"
            tabIndex={0}
            onClick={handleUploadImageClick}
            onKeyDown={handleKeyDown}
          >
            {messages.uploadBtnTitle}
          </Button>
        </Form.Label>

        {errors.image === messages.imageSize && (
          <Form.Control.Feedback type="invalid" className="manage-entity-modal-feedback mt-1">
            {errors.image}
          </Form.Control.Feedback>
        )}

        {isValidationTriggered && !imagePreview && (
          <Form.Control.Feedback type="invalid" className="manage-entity-modal-feedback mt-1">
            {messages.imageRequiredText}
          </Form.Control.Feedback>
        )}

        {imagePreview && (
          <Figure className="mt-3 mb-0 d-block">
            <Figure.Image
              className="entity-image-preview mb-0"
              alt={messages.entityPreviewScreenReaderText}
              src={imagePreview}
            />
          </Figure>
        )}
      </Form.Group>
    </div>
  );
};

EntityImage.propTypes = {
  imagePreview: PropTypes.string,
  handleImageUpload: PropTypes.func.isRequired,
};

export default EntityImage;

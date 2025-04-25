import React, { useState, useRef } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import {
  Form, Button, Figure, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import { useFormikContext } from 'formik';

import messages from '../../../i18n';
import { MAX_IMAGE_SIZE } from '../constants';

const EntityImage = ({ imagePreview, handleImageUpload, acceptedImageFormats }) => {
  const intl = useIntl();
  const { values, errors } = useFormikContext();
  const [isValidationTriggered, setIsValidationTriggered] = useState(false);
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });
  const imageSrc = imagePreview || (
    typeof values.image === 'string' && !values.image.startsWith('blob:') ? values.image : null
  );

  const fileInputRef = useRef(null);

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
      <h3 className="h4 mb-3">{intl.formatMessage(messages.modalEntityImageHeadingText)}</h3>
      <Form.Group className="mb-4" controlId="formEntityImage" size={isExtraSmall ? null : 'sm'}>
        <Form.Control
          ref={fileInputRef}
          id="entity-image-upload"
          type="file"
          accept={acceptedImageFormats.join(', ')}
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
            {intl.formatMessage(messages.modalEntityImageBtnUploadText)}
          </Button>
        </Form.Label>

        {errors.image === intl.formatMessage(messages.modalEntityValidationImageSizeText, {
          maxSize: MAX_IMAGE_SIZE,
        }) && (
          <Form.Control.Feedback type="invalid" className="manage-entity-modal-feedback mt-1">
            {errors.image}
          </Form.Control.Feedback>
        )}

        {isValidationTriggered && !imagePreview && (
          <Form.Control.Feedback type="invalid" className="manage-entity-modal-feedback mt-1">
            {intl.formatMessage(messages.modalEntityValidationImageRequiredText)}
          </Form.Control.Feedback>
        )}

        {imageSrc && (
          <Figure className="mt-3 mb-0 d-block">
            <Figure.Image
              className="entity-image-preview mb-0"
              alt={intl.formatMessage(messages.modalEntityImagePreviewText)}
              src={imageSrc}
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
  acceptedImageFormats: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default EntityImage;

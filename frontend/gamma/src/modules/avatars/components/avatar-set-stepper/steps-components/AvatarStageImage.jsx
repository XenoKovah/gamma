import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Image, Dropzone, Button } from '@openedx/paragon';

import { readFileAsDataURL } from '../utils';
import { MAX_IMAGE_SIZE, ACCEPTED_IMAGE_FORMATS } from './constants';

import moduleMessages from '../../../i18n';

const AvatarStageImage = ({
  index, onRemove, setFieldValue, values,
}) => {
  const intl = useIntl();
  const avatarStageTitle = intl.formatMessage(moduleMessages.avatarSetStepperEvolutionAvatarStageTitle, {
    index: index + 1,
  });

  const getAvatarData = (idx, image) => ({
    title: intl.formatMessage(moduleMessages.avatarSetStepperEvolutionAvatarDefaultTitle, {
      index: idx + 1,
    }),
    description: intl.formatMessage(moduleMessages.avatarSetStepperEvolutionAvatarDefaultDescription, {
      index: idx + 1,
    }),
    image,
  });

  const handleProcessUpload = useCallback(async ({ fileData, handleError }) => {
    try {
      const file = fileData.get('file');
      const image = await readFileAsDataURL(file);
      const updatedAvatars = [...values.avatars];
      updatedAvatars[index] = getAvatarData(index, image);
      setFieldValue('avatars', updatedAvatars);
    } catch (error) {
      handleError(error);
    }
  }, [index, setFieldValue, values.avatars, intl]);

  return (
    <div className="avatar-stage-image">
      <h3 className="avatar-stage-image-title">{avatarStageTitle}</h3>
      {values.avatars[index]?.image ? (
        <Image
          className="avatar-stage-image-preview"
          src={values.avatars[index].image}
          fluid
          alt={avatarStageTitle}
        />
      ) : (
        <Dropzone
          onProcessUpload={handleProcessUpload}
          progressVariant="bar"
          maxSize={MAX_IMAGE_SIZE}
          accept={ACCEPTED_IMAGE_FORMATS}
        />
      )}
      <Button
        className="avatar-stage-image-remove-btn mt-2"
        variant="outline-secondary"
        onClick={onRemove}
        block
        size="sm"
      >
        {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionRemoveAvatarBtn)}
      </Button>
    </div>
  );
};

AvatarStageImage.propTypes = {
  index: PropTypes.number.isRequired,
  onRemove: PropTypes.func.isRequired,
  setFieldValue: PropTypes.func.isRequired,
  values: PropTypes.shape({
    avatars: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string,
        description: PropTypes.string,
        image: PropTypes.string, // Base64 data
      }),
    ),
  }).isRequired,
};

export default AvatarStageImage;

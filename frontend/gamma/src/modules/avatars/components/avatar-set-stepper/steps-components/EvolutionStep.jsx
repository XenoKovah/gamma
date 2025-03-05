import React, { useCallback } from 'react';
import { useIntl } from 'react-intl';
import { Formik } from 'formik';
import PropTypes from 'prop-types';
import {
  Stepper, Button, ActionRow, CardGrid,
} from '@openedx/paragon';
import { Add as AddIcon } from '@openedx/paragon/icons';

import { useAvatarsContext } from '../../../context/AvatarsContext';
import { StatusButton } from '../../../../../generic';
import { STEPPER_STEPS } from '../constants';
import AvatarStageImage from './AvatarStageImage';
import { DEFAULT_AVATAR_DATA } from './constants';

import moduleMessages from '../../../i18n';

const MIN_AVATARS_COUNT = 2;
const MAX_AVATARS_COUNT = 5;

const EvolutionStep = ({
  currentStep,
  submitStatus,
  setCurrentStep,
  statefulButtonLabels,
  handleUpdateAvatarSet,
}) => {
  const intl = useIntl();
  const { currentAvatarSetData, setCurrentAvatarSetData } = useAvatarsContext();
  const isCurrentStep = currentStep === STEPPER_STEPS.evolution;

  const handleAddAvatarStage = useCallback((formValues, setFieldValue) => {
    setFieldValue(STEPPER_STEPS.avatars, [...formValues.avatars, DEFAULT_AVATAR_DATA]);
  }, []);

  const handleRemoveAvatarStage = useCallback((formValues, setFieldValue, idx) => {
    const updatedAvatars = formValues.avatars.filter((_, i) => i !== idx);
    setFieldValue(STEPPER_STEPS.avatars, updatedAvatars);
  }, []);

  const handleAvatarSetSubmit = (values) => {
    const updatedAvatarSet = { ...currentAvatarSetData, avatars: values.avatars };

    const isDataUnchanged = JSON.stringify(updatedAvatarSet.avatars) === JSON.stringify(currentAvatarSetData.avatars);

    if (isDataUnchanged) {
      return setCurrentStep(STEPPER_STEPS.avatars);
    }

    setCurrentAvatarSetData(updatedAvatarSet);
    return handleUpdateAvatarSet(updatedAvatarSet, () => setCurrentStep(STEPPER_STEPS.avatars));
  };

  return (
    <Formik
      initialValues={{ avatars: [DEFAULT_AVATAR_DATA] }}
      onSubmit={handleAvatarSetSubmit}
    >
      {({ values, handleSubmit, setFieldValue }) => {
        const avatarStages = values.avatars.map((_, index) => index);
        const isSubmitDisabled = values.avatars.length < MIN_AVATARS_COUNT
          || values.avatars.length > MAX_AVATARS_COUNT
          || values.avatars.some(avatar => !avatar.image);

        return (
          <>
            <Stepper.Step
              eventKey={STEPPER_STEPS.evolution}
              title={intl.formatMessage(moduleMessages.avatarSetStepperEvolutionStepTitle)}
            >
              <h2 className="mt-4">
                {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionStepTitle)}
              </h2>
              <p>
                {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionDescription)}
              </p>
              <CardGrid
                columnSizes={{ xs: 12, lg: 6, xl: 4 }}
                hasEqualColumnHeights
              >
                {avatarStages.map((index) => (
                  <AvatarStageImage
                    key={index}
                    index={index}
                    setFieldValue={setFieldValue}
                    values={values}
                    onRemove={() => handleRemoveAvatarStage(values, setFieldValue, index)}
                  />
                ))}
                <Button
                  iconBefore={AddIcon}
                  variant="outline-secondary"
                  onClick={() => handleAddAvatarStage(values, setFieldValue)}
                  className="add-avatar-stage-btn"
                >
                  {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionAddStageBtn)}
                </Button>
              </CardGrid>
            </Stepper.Step>

            {isCurrentStep && (
              <ActionRow className="justify-content-between">
                <Button variant="outline-primary" onClick={() => setCurrentStep(STEPPER_STEPS.title)}>
                  {intl.formatMessage(moduleMessages.avatarSetStepperPreviousBtnTitle)}
                </Button>
                <StatusButton
                  variant="primary"
                  labels={statefulButtonLabels}
                  options={{
                    submitStatus,
                    submitFn: handleSubmit,
                    disabled: isSubmitDisabled,
                  }}
                />
              </ActionRow>
            )}
          </>
        );
      }}
    </Formik>
  );
};

EvolutionStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  handleUpdateAvatarSet: PropTypes.func.isRequired,
  submitStatus: PropTypes.string,
  statefulButtonLabels: PropTypes.shape({
    default: PropTypes.string.isRequired,
    pending: PropTypes.string.isRequired,
    complete: PropTypes.string.isRequired,
    finish: PropTypes.string.isRequired,
  }).isRequired,
};

export default EvolutionStep;

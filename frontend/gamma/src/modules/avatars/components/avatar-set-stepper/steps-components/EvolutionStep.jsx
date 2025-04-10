import React, { useCallback } from 'react';
import { useIntl } from 'react-intl';
import { Formik } from 'formik';
import PropTypes from 'prop-types';
import { Stepper, Button, CardGrid } from '@openedx/paragon';
import { Add as AddIcon } from '@openedx/paragon/icons';

import { useAvatarsContext } from '../../../context/AvatarsContext';
import { convertImageToBase64 } from '../../../data';
import { STEPPER_STEPS } from '../constants';
import AvatarStageImage from './AvatarStageImage';
import { DEFAULT_AVATAR_DATA, MIN_AVATARS_COUNT, MAX_AVATARS_COUNT } from './constants';
import StepFooter from './StepFooter';

import moduleMessages from '../../../i18n';

const EvolutionStep = ({
  currentStep,
  submitStatus,
  setCurrentStep,
  statefulButtonLabels,
  handleUpdateAvatarSet,
  handleCloseManageAvatarSetModal,
}) => {
  const intl = useIntl();
  const { currentAvatarSetData, setCurrentAvatarSetData } = useAvatarsContext();
  const isCurrentStep = currentStep === STEPPER_STEPS.evolution;

  const handleAddAvatarStage = useCallback((formValues, setFieldValue) => {
    setFieldValue(STEPPER_STEPS.avatars, [...(formValues.avatars || []), DEFAULT_AVATAR_DATA]);
  }, []);

  const handleRemoveAvatarStage = useCallback((formValues, setFieldValue, idx) => {
    const updatedAvatars = formValues.avatars.filter((_, i) => i !== idx);
    setFieldValue(STEPPER_STEPS.avatars, updatedAvatars);
  }, []);

  const handleAvatarSetSubmit = async (values) => {
    try {
      const updatedAvatars = await Promise.all(
        values.avatars.map(async (avatar) => ({
          ...avatar,
          image: await convertImageToBase64(avatar.image),
        })),
      );

      const updatedAvatarSet = { ...currentAvatarSetData, avatars: updatedAvatars };

      if (JSON.stringify(values.avatars) === JSON.stringify(currentAvatarSetData.avatars)) {
        setCurrentStep(STEPPER_STEPS.avatars);
        return;
      }

      setCurrentAvatarSetData(updatedAvatarSet);
      await handleUpdateAvatarSet(updatedAvatarSet);
      setCurrentStep(STEPPER_STEPS.avatars);
    } catch (error) {
      console.error('Error updating avatar set:', error); // eslint-disable-line no-console
    }
  };

  return (
    <Formik
      initialValues={{
        avatars: Array.isArray(currentAvatarSetData?.avatars) ? currentAvatarSetData.avatars : [DEFAULT_AVATAR_DATA],
      }}
      enableReinitialize
      onSubmit={handleAvatarSetSubmit}
    >
      {({ values, handleSubmit, setFieldValue }) => {
        const avatarStages = (values.avatars ?? []).map((_, index) => index);
        const isSubmitDisabled = values.avatars.length < MIN_AVATARS_COUNT
          || values.avatars.length > MAX_AVATARS_COUNT
          || values.avatars.some(avatar => !avatar.image);
        const isAddPresetBtnDisabled = values.avatars.length >= MAX_AVATARS_COUNT
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
                  disabled={isAddPresetBtnDisabled}
                >
                  {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionAddStageBtn)}
                </Button>
              </CardGrid>
            </Stepper.Step>

            {isCurrentStep && (
              <StepFooter
                prevBtnText={intl.formatMessage(moduleMessages.avatarSetStepperPreviousBtnTitle)}
                prevBtnOnClick={() => setCurrentStep(STEPPER_STEPS.title)}
                isStatefulBtn
                submitFn={handleSubmit}
                disabledNextBtn={isSubmitDisabled}
                statefulButtonLabels={statefulButtonLabels}
                submitStatus={submitStatus}
                closeBtnOnClick={handleCloseManageAvatarSetModal}
              />
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
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
};

export default EvolutionStep;

import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Formik } from 'formik';
import {
  Stepper, Form, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import * as Yup from 'yup';

import { useAvatarsContext } from '../../../context/AvatarsContext';
import { STEPPER_STEPS } from '../constants';
import StepFooter from './StepFooter';

import moduleMessages from '../../../i18n';

const TitleStep = ({
  currentStep,
  submitStatus,
  setCurrentStep,
  validationSchema,
  statefulButtonLabels,
  handleUpdateAvatarSet,
  handleCreateNewAvatarSet,
  handleCloseManageAvatarSetModal,
}) => {
  const intl = useIntl();
  const { currentAvatarSetData, setCurrentAvatarSetData } = useAvatarsContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.small.maxWidth });

  const proceedToNextStep = () => setCurrentStep(STEPPER_STEPS.evolution);

  const handleSubmitAvatarSet = (values) => {
    const updatedAvatarSet = { ...currentAvatarSetData, title: values.title };
    if (Array.isArray(updatedAvatarSet.avatars) && !updatedAvatarSet.avatars.length) {
      delete updatedAvatarSet.avatars;
    }

    setCurrentAvatarSetData(updatedAvatarSet);

    return currentAvatarSetData
      ? handleUpdateAvatarSet({ id: currentAvatarSetData.id, title: values.title }, proceedToNextStep)
      : handleCreateNewAvatarSet(values, proceedToNextStep);
  };

  return (
    <Formik
      initialValues={{ title: currentAvatarSetData?.title || '' }}
      enableReinitialize
      validationSchema={validationSchema}
      onSubmit={handleSubmitAvatarSet}
    >
      {({
        values, handleChange, handleBlur, errors,
        touched, dirty, isValid, handleSubmit, setFieldValue,
      }) => {
        const isTitleUnchanged = currentAvatarSetData?.title === values.title;

        const handleTrimmedBlur = (fieldName) => {
          setFieldValue(fieldName, values[fieldName].trim(), true);
          handleBlur({ target: { name: fieldName } });
        };

        return (
          <>
            <Stepper.Step
              className={isExtraSmall ? 'w-100' : 'w-50'}
              eventKey={STEPPER_STEPS.title}
              title={intl.formatMessage(moduleMessages.avatarSetStepperTitleStepTitle)}
            >
              <h2 className="mt-4">
                {intl.formatMessage(moduleMessages.avatarSetStepperTitleStepTitle)}
              </h2>
              <p>{intl.formatMessage(moduleMessages.avatarSetStepperTitleStepDescription)}</p>
              <Form.Group>
                <Form.Control
                  floatingLabel={intl.formatMessage(moduleMessages.avatarSetStepperTitleStepInputTitleLabel)}
                  isInvalid={!isTitleUnchanged && touched.title && !!errors.title}
                  onChange={handleChange}
                  onBlur={() => handleTrimmedBlur('title')}
                  value={values.title}
                  name="title"
                />
                {!isTitleUnchanged && touched.title && errors.title && (
                  <Form.Control.Feedback type="invalid">{errors.title}</Form.Control.Feedback>
                )}
              </Form.Group>
            </Stepper.Step>

            {currentStep === STEPPER_STEPS.title && (
              <StepFooter
                prevBtnText={intl.formatMessage(moduleMessages.avatarSetStepperCloseBtnTitle)}
                prevBtnOnClick={handleCloseManageAvatarSetModal}
                isStatefulBtn
                submitFn={isTitleUnchanged ? proceedToNextStep : handleSubmit}
                disabledNextBtn={!isTitleUnchanged && (!isValid || !dirty)}
                statefulButtonLabels={statefulButtonLabels}
                submitStatus={submitStatus}
              />
            )}
          </>
        );
      }}
    </Formik>
  );
};

TitleStep.propTypes = {
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
  submitStatus: PropTypes.string,
  currentStep: PropTypes.string.isRequired,
  statefulButtonLabels: PropTypes.shape({
    default: PropTypes.string.isRequired,
    pending: PropTypes.string.isRequired,
    complete: PropTypes.string.isRequired,
    finish: PropTypes.string.isRequired,
  }).isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  handleCreateNewAvatarSet: PropTypes.func.isRequired,
  handleUpdateAvatarSet: PropTypes.func.isRequired,
  validationSchema: PropTypes.instanceOf(Yup.ObjectSchema).isRequired,
};

TitleStep.defaultProps = {
  submitStatus: '',
};

export default TitleStep;

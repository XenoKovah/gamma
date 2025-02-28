import React, { useEffect } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Formik } from 'formik';
import {
  Stepper, Button, ActionRow, Form, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import * as Yup from 'yup';

import { StatusButton } from '../../../../../generic';
import { STEPPER_STEPS } from '../constants';

import moduleMessages from '../../../i18n';

const TitleStep = ({
  currentStep,
  submitStatus,
  setCurrentStep,
  validationSchema,
  statefulButtonLabels,
  handleCreateNewAvatarSet,
  handleCloseManageAvatarSetModal,
  showAvatarSetCreatedSuccessfully,
}) => {
  const intl = useIntl();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.small.maxWidth });

  useEffect(() => {
    if (showAvatarSetCreatedSuccessfully) {
      setCurrentStep(STEPPER_STEPS.configuration);
    }
  }, [showAvatarSetCreatedSuccessfully, setCurrentStep]);

  return (
    <Formik
      initialValues={{ title: '' }}
      validationSchema={validationSchema}
      onSubmit={(values) => handleCreateNewAvatarSet(values)}
    >
      {({
        values, handleChange, handleBlur, errors, touched, dirty, isValid, handleSubmit,
      }) => (
        <>
          <Stepper.Step
            className={isExtraSmall ? 'w-100' : 'w-50'}
            eventKey={STEPPER_STEPS.title}
            title={intl.formatMessage(moduleMessages.avatarStepperTitleStepTitle)}
          >
            <h2 className="mt-4">
              {intl.formatMessage(moduleMessages.avatarStepperTitleStepTitle)}
            </h2>
            <p>
              {intl.formatMessage(moduleMessages.avatarStepperTitleStepDescription)}
            </p>
            <Form.Group>
              <Form.Control
                floatingLabel={intl.formatMessage(moduleMessages.avatarStepperTitleStepInputTitleLabel)}
                isInvalid={touched.title && !!errors.title}
                onChange={handleChange}
                onBlur={handleBlur}
                value={values.title}
                name={STEPPER_STEPS.title}
              />
              {touched.title && !!errors.title && (
                <Form.Control.Feedback type="invalid">
                  {errors.title}
                </Form.Control.Feedback>
              )}
            </Form.Group>
          </Stepper.Step>
          {currentStep === STEPPER_STEPS.title && (
            <ActionRow className="justify-content-between">
              <Button variant="outline-primary" onClick={handleCloseManageAvatarSetModal}>
                {intl.formatMessage(moduleMessages.avatarStepperCloseBtnTitle)}
              </Button>
              <StatusButton
                variant="primary"
                labels={statefulButtonLabels}
                options={{
                  submitStatus,
                  submitFn: handleSubmit,
                  disabled: !isValid || !dirty,
                }}
              />
            </ActionRow>
          )}
        </>
      )}
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
  showAvatarSetCreatedSuccessfully: PropTypes.bool.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  handleCreateNewAvatarSet: PropTypes.func.isRequired,
  validationSchema: PropTypes.instanceOf(Yup.ObjectSchema).isRequired,
};

TitleStep.defaultProps = {
  submitStatus: '',
};

export default TitleStep;

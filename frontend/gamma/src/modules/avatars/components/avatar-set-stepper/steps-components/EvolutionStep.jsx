import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Stepper, Button, ActionRow } from '@openedx/paragon';

import { StatusButton } from '../../../../../generic';
import { STEPPER_STEPS } from '../constants';

import moduleMessages from '../../../i18n';

const EvolutionStep = ({
  currentStep,
  setCurrentStep,
  handleCloseManageAvatarSetModal,
  statefulButtonLabels,
}) => {
  const intl = useIntl();

  return (
    <>
      <Stepper.Step
        eventKey={STEPPER_STEPS.evolution}
        title={intl.formatMessage(moduleMessages.avatarSetStepperEvolutionStepTitle)}
      >
        <h2 className="mt-4">
          {intl.formatMessage(moduleMessages.avatarSetStepperEvolutionStepTitle)}
        </h2>
      </Stepper.Step>
      {currentStep === STEPPER_STEPS.evolution && (
        <ActionRow className="justify-content-between">
          <Button variant="outline-primary" onClick={handleCloseManageAvatarSetModal}>
            {intl.formatMessage(moduleMessages.avatarSetStepperCloseBtnTitle)}
          </Button>
          <StatusButton
            variant="primary"
            labels={statefulButtonLabels}
            options={{
              submitStatus: 'default',
              submitFn: () => setCurrentStep(STEPPER_STEPS.avatars),
              disabled: false,
            }}
          />
        </ActionRow>
      )}
    </>
  );
};

EvolutionStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
  statefulButtonLabels: PropTypes.shape({
    default: PropTypes.string.isRequired,
    pending: PropTypes.string.isRequired,
    complete: PropTypes.string.isRequired,
    finish: PropTypes.string.isRequired,
  }).isRequired,
};

export default EvolutionStep;

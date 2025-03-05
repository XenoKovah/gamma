import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Stepper, Button, ActionRow } from '@openedx/paragon';

import { STEPPER_STEPS } from '../constants';

import moduleMessages from '../../../i18n';

const AvatarsStep = ({ currentStep, handleCloseManageAvatarSetModal, setCurrentStep }) => {
  const intl = useIntl();

  return (
    <>
      <Stepper.Step
        eventKey={STEPPER_STEPS.avatars}
        title={intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
      >
        <h2 className="mt-4">
          {intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
        </h2>
      </Stepper.Step>
      {currentStep === STEPPER_STEPS.avatars && (
        <ActionRow className="justify-content-between">
          <Button variant="outline-primary" onClick={() => setCurrentStep(STEPPER_STEPS.evolution)}>
            {intl.formatMessage(moduleMessages.avatarSetStepperPreviousBtnTitle)}
          </Button>
          <Button onClick={handleCloseManageAvatarSetModal}>
            {intl.formatMessage(moduleMessages.avatarSetStepperBtnFinishText)}
          </Button>
        </ActionRow>
      )}
    </>
  );
};

AvatarsStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
};

export default AvatarsStep;

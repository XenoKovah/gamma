import React from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Stepper, Button, ActionRow } from '@openedx/paragon';

import { STEPPER_STEPS } from '../constants';

import moduleMessages from '../../../i18n';

const AvatarsStep = ({ currentStep, handleCloseManageAvatarSetModal }) => {
  const intl = useIntl();

  return (
    <>
      <Stepper.Step
        eventKey={STEPPER_STEPS.avatars}
        title={intl.formatMessage(moduleMessages.avatarStepperAvatarsStepTitle)}
      >
        <h2 className="mt-4">
          {intl.formatMessage(moduleMessages.avatarStepperAvatarsStepTitle)}
        </h2>
      </Stepper.Step>
      {currentStep === STEPPER_STEPS.avatars && (
        <ActionRow className="justify-content-between">
          <Button variant="outline-primary" onClick={handleCloseManageAvatarSetModal}>
            {intl.formatMessage(moduleMessages.avatarStepperCloseBtnTitle)}
          </Button>
          <Button onClick={handleCloseManageAvatarSetModal}>
            {intl.formatMessage(moduleMessages.avatarStepperBtnFinishText)}
          </Button>
        </ActionRow>
      )}
    </>
  );
};

AvatarsStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
};

export default AvatarsStep;

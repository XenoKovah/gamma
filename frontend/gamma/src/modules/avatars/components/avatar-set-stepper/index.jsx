import React, { useState, useMemo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Stepper, Container, FullscreenModal } from '@openedx/paragon';

import { EvolutionStep, TitleStep, AvatarsStep } from './steps-components';
import { stepTitleValidationSchema } from './validation';
import { SUBMIT_STATUSES, STEPPER_STEPS } from './constants';

import moduleMessages from '../../i18n';

export const AvatarSetStepper = ({
  submitStatus,
  avatarSetsData,
  handleCreateNewAvatarSet,
  closeManageAvatarSetModal,
  isManageAvatarSetModalOpen,
  showAvatarSetCreatedSuccessfully,
}) => {
  const intl = useIntl();
  const [currentStep, setCurrentStep] = useState(STEPPER_STEPS.title);
  const [stepperKey, setStepperKey] = useState(0);

  const handleCloseManageAvatarSetModal = () => {
    closeManageAvatarSetModal();
    setCurrentStep(STEPPER_STEPS.title);
    setStepperKey(prevKey => prevKey + 1);
  };

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isManageAvatarSetModalOpen) {
        handleCloseManageAvatarSetModal();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isManageAvatarSetModalOpen, handleCloseManageAvatarSetModal]);

  const statefulButtonLabels = {
    default: intl.formatMessage(moduleMessages.avatarSetStepperBtnStatefulDefaultText),
    pending: intl.formatMessage(moduleMessages.avatarSetStepperBtnStatefulPendingText),
    complete: intl.formatMessage(moduleMessages.avatarSetStepperBtnStatefulCompleteText),
    finish: intl.formatMessage(moduleMessages.avatarSetStepperBtnFinishText),
  };

  const translations = {
    validation: {
      titleStep: {
        titleRequired: intl.formatMessage(moduleMessages.avatarSetStepperValidationTitleRequired),
        titleMaxLength: intl.formatMessage(moduleMessages.avatarSetStepperValidationTitleMaxLength),
        titleLettersNumbers: intl.formatMessage(moduleMessages.avatarSetStepperValidationTitleLettersNumbers),
        titleUnique: intl.formatMessage(moduleMessages.avatarSetStepperValidationTitleUnique),
      },
    },
  };

  const avatarTitleMap = useMemo(
    () => new Map(avatarSetsData.map(set => [set.title.toLowerCase(), set.id])),
    [avatarSetsData],
  );

  return (
    <Stepper key={stepperKey} activeKey={currentStep}>
      <FullscreenModal
        title={intl.formatMessage(moduleMessages.avatarSetStepperTitle)}
        className="avatar-set-stepper"
        // Prevents modal closure on outside clicks,
        // including interactions with floating notifications.
        isBlocking
        hasCloseButton={false}
        isOpen={isManageAvatarSetModalOpen}
        onClose={closeManageAvatarSetModal}
        isOverflowVisible
        beforeBodyNode={<Stepper.Header className="border-bottom border-light" />}
      >
        <Container className="avatar-set-stepper-container" size="md">
          <TitleStep
            currentStep={currentStep}
            submitStatus={submitStatus}
            setCurrentStep={setCurrentStep}
            statefulButtonLabels={statefulButtonLabels}
            handleCloseManageAvatarSetModal={handleCloseManageAvatarSetModal}
            showAvatarSetCreatedSuccessfully={showAvatarSetCreatedSuccessfully}
            validationSchema={stepTitleValidationSchema(translations.validation.titleStep, avatarTitleMap)}
            handleCreateNewAvatarSet={handleCreateNewAvatarSet}
          />
          <EvolutionStep
            currentStep={currentStep}
            setCurrentStep={setCurrentStep}
            statefulButtonLabels={statefulButtonLabels}
            handleCloseManageAvatarSetModal={handleCloseManageAvatarSetModal}
          />
          <AvatarsStep
            currentStep={currentStep}
            setCurrentStep={setCurrentStep}
            handleCloseManageAvatarSetModal={handleCloseManageAvatarSetModal}
          />
        </Container>
      </FullscreenModal>
    </Stepper>
  );
};

AvatarSetStepper.propTypes = {
  isManageAvatarSetModalOpen: PropTypes.bool.isRequired,
  closeManageAvatarSetModal: PropTypes.func.isRequired,
  handleCreateNewAvatarSet: PropTypes.func.isRequired,
  submitStatus: PropTypes.oneOf(SUBMIT_STATUSES).isRequired,
  showAvatarSetCreatedSuccessfully: PropTypes.bool.isRequired,
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      title: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

export default AvatarSetStepper;

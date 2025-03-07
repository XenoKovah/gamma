import React, { useState, useMemo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Stepper, Container, FullscreenModal } from '@openedx/paragon';

import { useAvatarsContext } from '../../context/AvatarsContext';
import { EvolutionStep, TitleStep, AvatarsStep } from './steps-components';
import { stepTitleValidationSchema } from './validation';
import { SUBMIT_STATUSES, STEPPER_STEPS } from './constants';

import moduleMessages from '../../i18n';

export const AvatarSetStepper = ({
  coursesData,
  actionsData,
  submitStatus,
  avatarSetsData,
  deletionStatus,
  setSubmitStatus,
  organizationsData,
  handleUpdateAvatar,
  handleDeleteAvatar,
  handleCreateNewAvatarSet,
  closeManageAvatarSetModal,
  isManageAvatarSetModalOpen,
  handleUpdateAvatarSet,
}) => {
  const intl = useIntl();
  const { setCurrentAvatarSetData } = useAvatarsContext();
  const [currentStep, setCurrentStep] = useState(STEPPER_STEPS.title);
  const [stepperKey, setStepperKey] = useState(0);

  const handleCloseManageAvatarSetModal = () => {
    closeManageAvatarSetModal();
    setCurrentStep(STEPPER_STEPS.title);
    setStepperKey(prevKey => prevKey + 1);
    setCurrentAvatarSetData(null);
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
            validationSchema={stepTitleValidationSchema(translations.validation.titleStep, avatarTitleMap)}
            handleCreateNewAvatarSet={handleCreateNewAvatarSet}
            handleUpdateAvatarSet={handleUpdateAvatarSet}
          />
          <EvolutionStep
            currentStep={currentStep}
            submitStatus={submitStatus}
            setCurrentStep={setCurrentStep}
            statefulButtonLabels={statefulButtonLabels}
            handleCloseManageAvatarSetModal={handleCloseManageAvatarSetModal}
            handleUpdateAvatarSet={handleUpdateAvatarSet}
          />
          <AvatarsStep
            currentStep={currentStep}
            setCurrentStep={setCurrentStep}
            avatarSetsData={avatarSetsData}
            handleCloseManageAvatarSetModal={handleCloseManageAvatarSetModal}
            handleDeleteAvatar={handleDeleteAvatar}
            submitStatus={submitStatus}
            deletionStatus={deletionStatus}
            setSubmitStatus={setSubmitStatus}
            coursesData={coursesData}
            organizationsData={organizationsData}
            actionsData={actionsData}
            handleUpdateAvatar={handleUpdateAvatar}
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
  handleUpdateAvatarSet: PropTypes.func.isRequired,
  submitStatus: PropTypes.oneOf(SUBMIT_STATUSES).isRequired,
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      title: PropTypes.string.isRequired,
    }),
  ).isRequired,
  coursesData: PropTypes.shape({
    courses: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  organizationsData: PropTypes.shape({
    organisations: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  actionsData: PropTypes.arrayOf(PropTypes.shape({
    eventType: PropTypes.string.isRequired,
  })),
  handleUpdateAvatar: PropTypes.func.isRequired,
  handleDeleteAvatar: PropTypes.func.isRequired,
  deletionStatus: PropTypes.oneOf(SUBMIT_STATUSES).isRequired,
  setSubmitStatus: PropTypes.func.isRequired,
};

export default AvatarSetStepper;

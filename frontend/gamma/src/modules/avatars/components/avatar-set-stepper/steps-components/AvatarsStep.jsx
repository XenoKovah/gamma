import React, { useState, useMemo } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Stepper, CardGrid, useToggle } from '@openedx/paragon';

import { AlertModal, ManageEntityModal, Card as AvatarCard } from '../../../../../generic';
import { useAvatarsContext } from '../../../context/AvatarsContext';
import { STEPPER_STEPS } from '../constants';
import StepFooter from './StepFooter';

import moduleMessages from '../../../i18n';

const ACCEPTED_IMAGE_FORMATS = ['image/svg+xml'];

const AvatarsStep = ({
  currentStep,
  actionsData,
  coursesData,
  submitStatus,
  setCurrentStep,
  deletionStatus,
  avatarSetsData,
  setSubmitStatus,
  organizationsData,
  handleDeleteAvatar,
  handleUpdateAvatar,
  handleCloseManageAvatarSetModal,
}) => {
  const intl = useIntl();
  const { currentAvatarSetData } = useAvatarsContext();

  const [deletingAvatarId, setDeletingAvatarId] = useState();
  const [editingAvatarData, setEditingAvatarData] = useState(null);
  const [
    isDeletionAvatarModalOpen, openDeletionAvatarModal, closeDeletionAvatarModal,
  ] = useToggle(false);
  const [isManageEntityModalOpen, openManageEntityModal, closeManageEntityModal] = useToggle(false);

  const avatarSetsMap = useMemo(
    () => new Map(avatarSetsData.map(set => [set.id, set])),
    [avatarSetsData],
  );

  const selectedAvatarSet = avatarSetsMap.get(currentAvatarSetData?.id);

  const avatarsMap = useMemo(
    () => new Map(selectedAvatarSet?.avatars.map(avatar => [avatar.id, avatar])),
    [selectedAvatarSet?.avatars],
  );

  const handleOpenDeletionAvatarModal = (id) => {
    openDeletionAvatarModal();
    setDeletingAvatarId(id);
  };

  const handleOpenEditAvatarModal = (id) => {
    setEditingAvatarData(avatarsMap.get(id));
    openManageEntityModal();
  };

  return (
    <>
      <AlertModal
        title={intl.formatMessage(moduleMessages.confirmDeletionModalTitle)}
        isOpen={isDeletionAvatarModalOpen}
        onClose={closeDeletionAvatarModal}
        onDelete={() => handleDeleteAvatar(deletingAvatarId, closeDeletionAvatarModal)}
        description={intl.formatMessage(moduleMessages.confirmAvatarDeletionModalDescription)}
        isStatefulButton
        submitStatus={deletionStatus}
      />
      <ManageEntityModal
        isManageEntityModalOpen={isManageEntityModalOpen}
        title={intl.formatMessage(moduleMessages.editAvatarModalTitle)}
        data={{
          entityData: editingAvatarData,
          courses: coursesData?.courses || [],
          organizations: organizationsData?.organisations || [],
          actions: actionsData || [],
        }}
        submitForm={handleUpdateAvatar}
        submitStatus={submitStatus}
        setSubmitStatus={setSubmitStatus}
        onReset={closeManageEntityModal}
        entityAcceptedImageFormats={ACCEPTED_IMAGE_FORMATS}
      />
      <Stepper.Step
        eventKey={STEPPER_STEPS.avatars}
        title={intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
      >
        <h2 className="my-4">
          {intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
        </h2>
        {selectedAvatarSet?.avatars?.length > 0 && (
          <CardGrid columnSizes={{ xs: 12, lg: 6, xl: 4 }} hasEqualColumnHeights>
            {selectedAvatarSet.avatars.map(({ id, title, image }) => (
              <AvatarCard
                key={id}
                id={id}
                title={title}
                src={image}
                onPrevBtnClick={() => handleOpenDeletionAvatarModal(id)}
                onNextBtnClick={() => handleOpenEditAvatarModal(id)}
                prevBtnTitle={intl.formatMessage(moduleMessages.avatarDeleteBtnTitle)}
                nextBtnTitle={intl.formatMessage(moduleMessages.avatarEditBtnTitle)}
              />
            ))}
          </CardGrid>
        )}
      </Stepper.Step>

      {currentStep === STEPPER_STEPS.avatars && (
        <StepFooter
          prevBtnText={intl.formatMessage(moduleMessages.avatarSetStepperPreviousBtnTitle)}
          prevBtnOnClick={() => setCurrentStep(STEPPER_STEPS.evolution)}
          nextBtnText={intl.formatMessage(moduleMessages.avatarSetStepperBtnFinishText)}
          nextBtnOnClick={handleCloseManageAvatarSetModal}
        />
      )}
    </>
  );
};

AvatarsStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  coursesData: PropTypes.shape({
    courses: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  organizationsData: PropTypes.shape({
    organisations: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  actionsData: PropTypes.arrayOf(PropTypes.shape({
    eventType: PropTypes.string.isRequired,
  })),
  submitStatus: PropTypes.string.isRequired,
  deletionStatus: PropTypes.string.isRequired,
  setSubmitStatus: PropTypes.func.isRequired,
  handleDeleteAvatar: PropTypes.func.isRequired,
  handleUpdateAvatar: PropTypes.func.isRequired,
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      title: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

export default AvatarsStep;

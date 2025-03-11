import React, { useState, useMemo } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import {
  Stepper, CardGrid, useToggle,
} from '@openedx/paragon';

import {
  AlertModal, ManageEntityModal,
  Card as AvatarCard, SubHeader, AlertComponent,
} from '../../../../../generic';
import { useAvatarsContext } from '../../../context/AvatarsContext';
import { STEPPER_STEPS } from '../constants';
import {
  MAX_AVATARS_COUNT, MIN_AVATARS_COUNT, ACCEPTED_IMAGE_FORMATS,
} from './constants';
import StepFooter from './StepFooter';

import moduleMessages from '../../../i18n';

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
}) => {
  const intl = useIntl();
  const { currentAvatarSetData } = useAvatarsContext();
  const proceedToNextStep = () => setCurrentStep(STEPPER_STEPS.finish);

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

  const avatarsCount = selectedAvatarSet?.avatars?.length ?? 0;
  const isActionButtonDisabled = avatarsCount >= MAX_AVATARS_COUNT || avatarsCount < MIN_AVATARS_COUNT;

  const avatarsMap = useMemo(
    () => new Map(selectedAvatarSet?.avatars.map(avatar => [avatar.id, avatar])),
    [selectedAvatarSet?.avatars],
  );

  const handleOpenDeletionAvatarModal = (id) => {
    openDeletionAvatarModal();
    setDeletingAvatarId(id);
  };

  const handleOpenAvatarModal = (avatarId = null) => {
    setEditingAvatarData(avatarsMap.get(avatarId));
    openManageEntityModal();
  };

  // TODO: Move this sorting logic to a utility function
  const sortedAvatars = [...(selectedAvatarSet?.avatars || [])].sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
  );

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
          organizations: organizationsData?.organizations || [],
          actions: actionsData || [],
        }}
        submitForm={handleUpdateAvatar}
        submitStatus={submitStatus}
        setSubmitStatus={setSubmitStatus}
        onReset={closeManageEntityModal}
        entityAcceptedImageFormats={Object.keys(ACCEPTED_IMAGE_FORMATS)}
      />
      <Stepper.Step
        eventKey={STEPPER_STEPS.avatars}
        title={intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
      >
        <SubHeader
          isError={false}
          headingLevel="h2"
          title={intl.formatMessage(moduleMessages.avatarSetStepperAvatarsStepTitle)}
          description={
            intl.formatMessage(moduleMessages.totalAvatarsCount, {
              avatarsCount: selectedAvatarSet?.avatars?.length || 0,
            })
          }
        />
        {selectedAvatarSet?.avatars?.length < MIN_AVATARS_COUNT && (
          <AlertComponent
            title={intl.formatMessage(moduleMessages.alertEmptyAvatarsListTitle)}
            description={intl.formatMessage(moduleMessages.alertEmptyAvatarsListDescription)}
            variant="info"
          />
        )}
        {selectedAvatarSet?.avatars?.length > 0 && (
          <CardGrid columnSizes={{ xs: 12, lg: 6, xl: 4 }} hasEqualColumnHeights>
            {sortedAvatars.map(({ id, title, image }) => (
              <AvatarCard
                key={id}
                id={id}
                title={title}
                src={image}
                onPrevBtnClick={() => handleOpenDeletionAvatarModal(id)}
                onNextBtnClick={() => handleOpenAvatarModal(id)}
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
          nextBtnText={intl.formatMessage(moduleMessages.avatarSetStepperBtnStatefulDefaultText)}
          nextBtnOnClick={proceedToNextStep}
          disabledNextBtn={isActionButtonDisabled}
        />
      )}
    </>
  );
};

AvatarsStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  coursesData: PropTypes.shape({
    courses: PropTypes.arrayOf(PropTypes.string).isRequired,
  }),
  organizationsData: PropTypes.shape({
    organizations: PropTypes.arrayOf(PropTypes.string).isRequired,
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

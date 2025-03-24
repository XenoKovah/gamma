import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { useAvatarsContext } from '../../../context/AvatarsContext';
import { Card as AvatarSetCard } from '../../../../../generic';
import { avatarsPropTypes } from '../propTypes';

import messages from '../../../i18n';

import imagePlaceholder from '../../../assets/images/not-found.jpg';

const AvatarSetItem = ({
  openConfirmDeletionModal, openManageAvatarSetModal, avatarSetData, setIsEditStepperMode,
}) => {
  const intl = useIntl();
  const { setCurrentAvatarSetData } = useAvatarsContext();

  const getAvatarSetImage = (avatarsList, defaultImg) => {
    if (!avatarsList.length) {
      return defaultImg;
    }

    const latestAvatar = avatarsList.reduce(
      (avatarWithHighestId, currentAvatar) => (currentAvatar.id > avatarWithHighestId.id
        ? currentAvatar
        : avatarWithHighestId),
      avatarsList[0],
    );

    return latestAvatar.image || defaultImg;
  };

  const imageSrc = getAvatarSetImage(avatarSetData.avatars, imagePlaceholder);

  const handleOpenManageAvatarSetModal = (avatarSetParams) => {
    openManageAvatarSetModal();
    setIsEditStepperMode(true);
    setCurrentAvatarSetData(avatarSetParams);
  };

  return (
    <AvatarSetCard
      id={avatarSetData.id}
      title={avatarSetData.title}
      src={imageSrc}
      badgeText={avatarSetData.isDraft ? intl.formatMessage(messages.avatarSetDraftBadgeText) : undefined}
      prevBtnTitle={intl.formatMessage(messages.avatarSetDeleteBtnTitle)}
      nextBtnTitle={intl.formatMessage(messages.avatarSetEditBtnTitle)}
      onPrevBtnClick={() => openConfirmDeletionModal(avatarSetData.id)}
      onNextBtnClick={() => handleOpenManageAvatarSetModal(avatarSetData)}
    />
  );
};

AvatarSetItem.propTypes = {
  openConfirmDeletionModal: PropTypes.func.isRequired,
  openManageAvatarSetModal: PropTypes.func.isRequired,
  avatarSetData: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    avatars: PropTypes.arrayOf(avatarsPropTypes).isRequired,
    isDraft: PropTypes.bool.isRequired,
  }).isRequired,
  setIsEditStepperMode: PropTypes.func.isRequired,
};

export default AvatarSetItem;

import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { Card as AvatarSetCard } from '../../../../../generic';
import { avatarsPropTypes } from '../propTypes';

import messages from '../../../i18n';

import imagePlaceholder from '../../../assets/images/not-found.jpg';

const AvatarSetItem = ({
  id, title, avatars, isDraft, openConfirmDeletionModal,
}) => {
  const intl = useIntl();

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

  const imageSrc = getAvatarSetImage(avatars, imagePlaceholder);

  return (
    <AvatarSetCard
      id={id}
      title={title}
      src={imageSrc}
      badgeText={isDraft && intl.formatMessage(messages.avatarSetDraftBadgeText)}
      prevBtnTitle={intl.formatMessage(messages.avatarSetDeleteBtnTitle)}
      nextBtnTitle={intl.formatMessage(messages.avatarSetEditBtnTitle)}
      onPrevBtnClick={() => openConfirmDeletionModal(id)}
      onNextBtnClick={() => {}} // TODO: implement edit
    />
  );
};

AvatarSetItem.propTypes = {
  id: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  isDraft: PropTypes.bool.isRequired,
  avatars: PropTypes.arrayOf(avatarsPropTypes).isRequired,
  openConfirmDeletionModal: PropTypes.func.isRequired,
};

export default AvatarSetItem;

import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { Card as StudentAvatarCard } from '../../../../../generic';

import messages from '../../../i18n';

import imagePlaceholder from '../../../assets/images/not-found.jpg';

const AvatarItem = ({
  id, title, image, openConfirmDeletionModal,
}) => {
  const intl = useIntl();
  const imageSrc = image || imagePlaceholder;

  return (
    <StudentAvatarCard
      id={id}
      title={title}
      src={imageSrc}
      prevBtnTitle={intl.formatMessage(messages.avatarSetDeleteBtnTitle)}
      nextBtnTitle={intl.formatMessage(messages.avatarSetEditBtnTitle)}
      onPrevBtnClick={() => openConfirmDeletionModal(id)}
      onNextBtnClick={() => {}} // TODO: implement edit
      showFooterActionRow={false}
      isLocked
    />
  );
};

AvatarItem.propTypes = {
  id: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  image: PropTypes.string,
  openConfirmDeletionModal: PropTypes.func.isRequired,
};

export default AvatarItem;

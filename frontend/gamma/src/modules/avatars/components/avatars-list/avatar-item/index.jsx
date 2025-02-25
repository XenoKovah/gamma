import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { ActionRow, Button, Card } from '@openedx/paragon';

import messages from '../../../i18n';
import { avatarsPropTypes } from '../propTypes';

import imagePlaceholder from '../../../assets/images/not-found.jpg';

const AvatarItem = ({
  id, title, avatars, openConfirmDeletionModal,
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
    <Card className="avatar-item" data-testid={`avatar-item-${id}`}>
      <Card.ImageCap
        className="avatar-item-image"
        src={imageSrc}
        srcAlt={title}
      />
      <Card.Header className="avatar-item-header" title={title} />
      <Card.Footer>
        <ActionRow>
          <Button variant="tertiary" block onClick={() => openConfirmDeletionModal(id)}>
            {intl.formatMessage(messages.avatarDeleteBtnTitle)}
          </Button>
          <Button className="mt-0" block>
            {intl.formatMessage(messages.avatarEditBtnTitle)}
          </Button>
        </ActionRow>
      </Card.Footer>
    </Card>
  );
};

AvatarItem.propTypes = {
  id: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  avatars: PropTypes.arrayOf(avatarsPropTypes).isRequired,
  openConfirmDeletionModal: PropTypes.func.isRequired,
};

export default AvatarItem;

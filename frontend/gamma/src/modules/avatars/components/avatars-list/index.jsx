import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import AvatarItem from './avatar-item';
import { avatarsPropTypes } from './propTypes';

const AvatarsList = ({ avatarSetsData, openConfirmDeletionModal }) => {
  const intl = useIntl();

  if (!avatarSetsData.length) {
    return (
      <AlertComponent
        title={intl.formatMessage(messages.alertEmptyAvatarsListTitle)}
        description={intl.formatMessage(messages.alertEmptyAvatarsListDescription)}
        variant="info"
      />
    );
  }

  return (
    <CardGrid
      columnSizes={{ xs: 12, lg: 6, xl: 4 }}
      hasEqualColumnHeights
    >
      {avatarSetsData.map(({ id, title, avatar }) => (
        <AvatarItem
          key={id}
          id={id}
          title={title}
          avatars={avatar}
          openConfirmDeletionModal={openConfirmDeletionModal}
        />
      ))}
    </CardGrid>
  );
};

AvatarsList.propTypes = {
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      avatar: PropTypes.arrayOf(avatarsPropTypes).isRequired,
      useInCourses: PropTypes.arrayOf(PropTypes.string).isRequired,
      isDraft: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  openConfirmDeletionModal: PropTypes.func.isRequired,
};

export default AvatarsList;

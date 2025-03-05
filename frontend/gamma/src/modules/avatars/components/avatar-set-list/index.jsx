import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import AvatarSetItem from './avatar-set-item';
import { avatarsPropTypes } from './propTypes';

const AvatarSetList = ({ avatarSetsData, openConfirmDeletionModal }) => {
  const intl = useIntl();

  if (!avatarSetsData.length) {
    return (
      <AlertComponent
        title={intl.formatMessage(messages.alertEmptyAvatarSetListTitle)}
        description={intl.formatMessage(messages.alertEmptyAvatarSetListDescription)}
        variant="info"
      />
    );
  }

  return (
    <CardGrid
      columnSizes={{ xs: 12, lg: 6, xl: 4 }}
      hasEqualColumnHeights
    >
      {avatarSetsData.map(({ id, title, avatars }) => (
        <AvatarSetItem
          key={id}
          id={id}
          title={title}
          avatars={avatars}
          openConfirmDeletionModal={openConfirmDeletionModal}
        />
      ))}
    </CardGrid>
  );
};

AvatarSetList.propTypes = {
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      avatars: PropTypes.arrayOf(avatarsPropTypes).isRequired,
      useInCourses: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.string),
        PropTypes.object,
      ]),
      isDraft: PropTypes.bool.isRequired,
    }),
  ).isRequired,
  openConfirmDeletionModal: PropTypes.func.isRequired,
};

export default AvatarSetList;

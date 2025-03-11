import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import AvatarSetItem from './avatar-set-item';
import { avatarsPropTypes } from './propTypes';

const AvatarSetList = ({ avatarSetsData, openConfirmDeletionModal, openManageAvatarSetModal }) => {
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

  // TODO: Move this sorting logic to a utility function
  const sortedAvatarSets = [...avatarSetsData].sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
  );

  return (
    <CardGrid
      columnSizes={{ xs: 12, lg: 6, xl: 4 }}
      hasEqualColumnHeights
    >
      {sortedAvatarSets.map((avatarSet) => (
        <AvatarSetItem
          key={avatarSet.id}
          avatarSetData={avatarSet}
          openConfirmDeletionModal={openConfirmDeletionModal}
          openManageAvatarSetModal={openManageAvatarSetModal}
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
  openManageAvatarSetModal: PropTypes.func.isRequired,
};

export default AvatarSetList;

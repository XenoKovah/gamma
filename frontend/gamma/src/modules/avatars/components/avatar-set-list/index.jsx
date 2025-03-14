import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import { sortByDate } from '../../utils';
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

  const sortedAvatarSets = sortByDate(avatarSetsData, 'createdAt', true);

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

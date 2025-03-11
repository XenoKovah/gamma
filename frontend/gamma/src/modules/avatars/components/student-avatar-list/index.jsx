import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent, Card as StudentAvatarCard } from '../../../../generic';
import messages from '../../i18n';
import imagePlaceholder from '../../assets/images/not-found.jpg';
import { avatarsPropTypes } from './propTypes';

// TODO: temp solution to show student experience with avatars.
const StudentAvatarList = ({ studentAvatarData }) => {
  const intl = useIntl();

  if (!studentAvatarData.avatars.length) {
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
      {studentAvatarData.avatars.map(({ id, title, image }) => (
        <StudentAvatarCard
          key={id}
          id={id}
          title={title}
          src={image || imagePlaceholder}
          showFooterActionRow={false}
          isLocked={!studentAvatarData.achievements.achievedAvatarIds.includes(id)}
        />
      ))}
    </CardGrid>
  );
};

StudentAvatarList.propTypes = {
  studentAvatarData: PropTypes.shape({
    id: PropTypes.number.isRequired,
    achievements: PropTypes.arrayOf(PropTypes.string).isRequired,
    title: PropTypes.string.isRequired,
    avatars: PropTypes.arrayOf(avatarsPropTypes).isRequired,
    useInCourses: PropTypes.oneOfType([
      PropTypes.arrayOf(PropTypes.string),
      PropTypes.object,
    ]),
    isDraft: PropTypes.bool.isRequired,
  }).isRequired,
};

export default StudentAvatarList;

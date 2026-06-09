import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import { sortByDate } from '../../utils';
import BadgeItem from './badge-item';

const BadgesList = ({
  badgesData,
  openConfirmDeletionAlert,
  firstBadgeRef,
  handleOpenManageEntityModal,
  handleOpenAssignModal,
  handleOpenUnassignModal,
}) => {
  const intl = useIntl();

  const sortedBadges = sortByDate(badgesData, 'createdAt', true);

  return (
    <ul className="list-unstyled p-0">
      {sortedBadges.length ? (
        sortedBadges.map((badge, index) => (
          <li key={badge.id} ref={index === 0 ? firstBadgeRef : null}>
            <BadgeItem
              title={badge.title}
              description={badge.description}
              image={badge.image}
              slug={badge.slug}
              isActive={badge.isActive}
              openConfirmDeletionAlert={() => openConfirmDeletionAlert(badge.id)}
              handleOpenManageEntityModal={() => handleOpenManageEntityModal(badge.id)}
              handleOpenAssignModal={() => handleOpenAssignModal(badge.id)}
              handleOpenUnassignModal={() => handleOpenUnassignModal(badge.id)}
            />
          </li>
        ))
      ) : (
        <li>
          <AlertComponent
            title={intl.formatMessage(messages.alertEmptyBadgesListTitle)}
            description={intl.formatMessage(messages.alertEmptyBadgesListDescription)}
            variant="info"
          />
        </li>
      )}
    </ul>
  );
};

BadgesList.propTypes = {
  badgesData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string,
      description: PropTypes.string,
      image: PropTypes.string,
      slug: PropTypes.string,
    }),
  ).isRequired,
  openConfirmDeletionAlert: PropTypes.func,
  firstBadgeRef: PropTypes.shape({ current: PropTypes.instanceOf(Element) }),
  handleOpenManageEntityModal: PropTypes.func.isRequired,
  handleOpenAssignModal: PropTypes.func,
  handleOpenUnassignModal: PropTypes.func,
};

BadgesList.defaultProps = {
  openConfirmDeletionAlert: () => {},
  firstBadgeRef: null,
  handleOpenAssignModal: () => {},
  handleOpenUnassignModal: () => {},
};

export default BadgesList;

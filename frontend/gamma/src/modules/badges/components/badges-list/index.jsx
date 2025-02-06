import React from 'react';
import PropTypes from 'prop-types';

import { useTranslate } from '../../../../i18n/utils';
import { AlertComponent } from '../../../../generic';
import BadgeItem from './badge-item';

const BadgesList = ({ badgesData, openConfirmDeletionAlert }) => {
  const messages = {
    alertEmptyBadgesList: {
      title: useTranslate('modules.badges.alert.empty-badges-list.title'),
      description: useTranslate('modules.badges.alert.empty-badges-list.description'),
    },
  };

  return (
    <ul className="list-unstyled p-0">
      {badgesData.length ? (
        badgesData.map((badge) => (
          <li key={badge.id}>
            <BadgeItem
              title={badge.title}
              description={badge.description}
              image={badge.image}
              slug={badge.slug}
              openConfirmDeletionAlert={openConfirmDeletionAlert}
            />
          </li>
        ))
      ) : (
        <li>
          <AlertComponent
            title={messages.alertEmptyBadgesList.title}
            description={messages.alertEmptyBadgesList.description}
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
  openConfirmDeletionAlert: PropTypes.func.isRequired,
};

export default BadgesList;

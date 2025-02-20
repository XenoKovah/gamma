import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import BadgeItem from './badge-item';

const BadgesList = ({ badgesData, openConfirmDeletionAlert, firstBadgeRef }) => {
  const intl = useIntl();

  return (
    <ul className="list-unstyled p-0">
      {badgesData.length ? (
        badgesData.map((badge, index) => (
          <li key={badge.id} ref={index === 0 ? firstBadgeRef : null}>
            <BadgeItem
              title={badge.title}
              description={badge.description}
              image={badge.image}
              slug={badge.slug}
              openConfirmDeletionAlert={() => openConfirmDeletionAlert(badge.id)}
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
};

BadgesList.defaultProps = {
  openConfirmDeletionAlert: () => {},
  firstBadgeRef: null,
};

export default BadgesList;

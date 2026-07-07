import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Collapsible, Badge } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import { sortByDate, groupBadgesByCategory } from '../../utils';
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

  if (!badgesData.length) {
    return (
      <AlertComponent
        title={intl.formatMessage(messages.alertEmptyBadgesListTitle)}
        description={intl.formatMessage(messages.alertEmptyBadgesListDescription)}
        variant="info"
      />
    );
  }

  // Newest first within each category, then group by category so the (potentially
  // large) list stays manageable: every category is collapsed by default and the
  // admin expands the ones they want. Uncategorized badges group together, last.
  const sortedBadges = sortByDate(badgesData, 'createdAt', true);
  const groups = groupBadgesByCategory(
    sortedBadges,
    intl.formatMessage(messages.badgesUncategorizedLabel),
  );

  return (
    <div className="badges-by-category p-0">
      {groups.map((group, groupIndex) => (
        <Collapsible
          key={group.key}
          className="badge-category-group mb-3"
          defaultOpen={false}
          title={(
            <span className="d-flex align-items-center">
              <span className="badge-category-title">{group.label}</span>
              <Badge variant="light" className="ml-2">
                {intl.formatMessage(messages.badgesCategoryCount, { count: group.badges.length })}
              </Badge>
            </span>
          )}
        >
          <ul
            className="list-unstyled p-0 mb-0"
            ref={groupIndex === 0 ? firstBadgeRef : null}
          >
            {group.badges.map((badge) => (
              <li key={badge.id}>
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
            ))}
          </ul>
        </Collapsible>
      ))}
    </div>
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

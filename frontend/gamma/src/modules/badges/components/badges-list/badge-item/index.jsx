import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import {
  Button, Card, useMediaQuery, breakpoints, Badge,
} from '@openedx/paragon';

import messages from '../../../i18n';

const BadgeItem = ({
  title, description, image, openConfirmDeletionAlert, handleOpenManageEntityModal,
  handleOpenAssignModal, handleOpenUnassignModal, handleOpenExpiryModal, isActive, isExpiring,
}) => {
  const intl = useIntl();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  return (
    <Card className="badge-item mb-4" orientation={isExtraSmall ? 'vertical' : 'horizontal'}>
      <Card.ImageCap
        className="badge-item-img"
        src={image}
        srcAlt={title || intl.formatMessage(messages.badgeDefaultTitle)}
      />
      <Card.Section title={title || intl.formatMessage(messages.badgeDefaultTitle)}>
        <Badge className="mb-4" variant={isActive ? 'success' : 'warning'}>
          {isActive
            ? intl.formatMessage(messages.badgeActiveStatusText)
            : intl.formatMessage(messages.badgeDraftStatusText)}
        </Badge>
        <p className="badge-item-description">
          {description || intl.formatMessage(messages.badgeDefaultDescription)}
        </p>
      </Card.Section>
      <Card.Footer orientation="vertical">
        <Button onClick={handleOpenManageEntityModal}>
          {intl.formatMessage(messages.badgeEditBtnTitle)}
        </Button>
        <Button variant="outline-primary" onClick={handleOpenAssignModal}>
          {intl.formatMessage(messages.badgeAssignBtnTitle)}
        </Button>
        <Button variant="outline-primary" onClick={handleOpenUnassignModal}>
          {intl.formatMessage(messages.badgeUnassignBtnTitle)}
        </Button>
        {isExpiring && (
          <Button variant="outline-primary" onClick={handleOpenExpiryModal}>
            {intl.formatMessage(messages.badgeExpiryBtnTitle)}
          </Button>
        )}
        <Button variant="outline-secondary" onClick={openConfirmDeletionAlert}>
          {intl.formatMessage(messages.badgeDeleteBtnTitle)}
        </Button>
      </Card.Footer>
    </Card>
  );
};

BadgeItem.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  image: PropTypes.string,
  openConfirmDeletionAlert: PropTypes.func.isRequired,
  handleOpenManageEntityModal: PropTypes.func.isRequired,
  handleOpenAssignModal: PropTypes.func,
  handleOpenUnassignModal: PropTypes.func,
  handleOpenExpiryModal: PropTypes.func,
  isActive: PropTypes.bool.isRequired,
  isExpiring: PropTypes.bool,
};

BadgeItem.defaultProps = {
  title: '',
  description: '',
  image: null,
  handleOpenAssignModal: () => {},
  handleOpenUnassignModal: () => {},
  handleOpenExpiryModal: () => {},
  isExpiring: false,
};

export default BadgeItem;

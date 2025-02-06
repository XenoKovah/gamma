import React from 'react';
import PropTypes from 'prop-types';
import {
  Button, Card, useMediaQuery, breakpoints,
} from '@openedx/paragon';

import { useTranslate } from '../../../../../i18n/utils';

const BadgeItem = ({
  title, description, image, openConfirmDeletionAlert,
}) => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const messages = {
    default: {
      badgeTitle: useTranslate('modules.badges.badge-item.default.title'),
      badgeDescription: useTranslate('modules.badges.badge-item.default.description'),
    },
    actionBtns: {
      edit: useTranslate('modules.badges.badge-item.button.edit.title'),
      delete: useTranslate('modules.badges.badge-item.button.delete.title'),
    },
  };

  return (
    <Card className="badge-item mb-4" orientation={isExtraSmall ? 'vertical' : 'horizontal'}>
      <Card.ImageCap
        className="badge-item-img"
        src={image}
        srcAlt={title || messages.default.badgeTitle}
      />
      <Card.Section title={title || messages.default.badgeTitle}>
        {description || messages.default.badgeDescription}
      </Card.Section>
      <Card.Footer orientation="vertical">
        <Button>
          {messages.actionBtns.edit}
        </Button>
        <Button variant="danger" onClick={openConfirmDeletionAlert}>
          {messages.actionBtns.delete}
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
};

export default BadgeItem;

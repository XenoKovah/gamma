import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import {
  Button, Card, useMediaQuery, breakpoints,
} from '@openedx/paragon';

import messages from '../../../i18n';

const BadgeItem = ({
  title, description, image, openConfirmDeletionAlert,
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
        {description || intl.formatMessage(messages.badgeDefaultDescription)}
      </Card.Section>
      <Card.Footer orientation="vertical">
        <Button>
          {intl.formatMessage(messages.badgeEditBtnTitle)}
        </Button>
        <Button variant="danger" onClick={openConfirmDeletionAlert}>
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
};

export default BadgeItem;

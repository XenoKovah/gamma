import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Button, Card } from '@openedx/paragon';

import messages from '../../../i18n';

const AvatarItem = ({ title, imageSrc }) => {
  const intl = useIntl();

  return (
    <Card className="avatar-item">
      <Card.ImageCap
        className="avatar-item-image"
        src={imageSrc}
        srcAlt={title}
      />
      <Card.Header title={title} />
      <Card.Footer>
        <Button>
          {intl.formatMessage(messages.avatarEditBtnTitle)}
        </Button>
        <Button variant="danger">
          {intl.formatMessage(messages.avatarDeleteBtnTitle)}
        </Button>
      </Card.Footer>
    </Card>
  );
};

AvatarItem.propTypes = {
  title: PropTypes.string.isRequired,
  imageSrc: PropTypes.string.isRequired,
};

export default AvatarItem;

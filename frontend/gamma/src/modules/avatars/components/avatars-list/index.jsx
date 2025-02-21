import React from 'react';
import { useIntl } from 'react-intl';
import { CardGrid } from '@openedx/paragon';

import { AlertComponent } from '../../../../generic';
import messages from '../../i18n';
import AvatarItem from './avatar-item';

import avatar from '../../assets/images/avatar.png';

const AvatarsList = () => {
  const intl = useIntl();

  return (
    <>
      <AlertComponent
        title={intl.formatMessage(messages.alertEmptyAvatarsListTitle)}
        description={intl.formatMessage(messages.alertEmptyAvatarsListDescription)}
        variant="info"
      />
      <CardGrid
        columnSizes={{
          xs: 12,
          lg: 6,
          xl: 4,
        }}
        hasEqualColumnHeights
      >
        {[...Array(6)].map((_, index) => (
          <AvatarItem
            key={index} // eslint-disable-line react/no-array-index-key
            title="Avatar title"
            imageSrc={avatar}
          />
        ))}
      </CardGrid>
    </>
  );
};

export default AvatarsList;

import React from 'react';
import PropTypes from 'prop-types';
import {
  Button, Stack, useMediaQuery, breakpoints,
} from '@openedx/paragon';
import { useIntl } from 'react-intl';

import messages from '../../i18n';

const SubHeader = ({ isError, badgesCount, openManageEntityModal }) => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });
  const intl = useIntl();

  return (
    <header className="mt-4 mb-4">
      <Stack className="justify-content-between" direction={isExtraSmall ? 'vertical' : 'horizontal'}>
        <h1 className="mb-0">{intl.formatMessage(messages.pageTitle)}</h1>
        {!isError && (
          <Stack direction={isExtraSmall ? 'vertical' : 'horizontal'} gap={3}>
            <p className="m-0">
              {intl.formatMessage(messages.totalBadgesCount, { badgesCount })}
            </p>
            <Button onClick={openManageEntityModal}>
              {intl.formatMessage(messages.addBadgeBtnText)}
            </Button>
          </Stack>
        )}
      </Stack>
    </header>
  );
};

SubHeader.propTypes = {
  isError: PropTypes.bool.isRequired,
  badgesCount: PropTypes.number.isRequired,
  openManageEntityModal: PropTypes.func.isRequired,
};

export default SubHeader;

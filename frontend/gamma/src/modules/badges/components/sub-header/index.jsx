import React from 'react';
import PropTypes from 'prop-types';
import {
  Button, Stack, useMediaQuery, breakpoints,
} from '@openedx/paragon';

import { useTranslate } from '../../../../i18n/utils';

const SubHeader = ({ isError, badgesCount, openBadgeModalDialog }) => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const messages = {
    headingText: useTranslate('modules.badges.heading.text'),
    totalBadges: {
      counterText: useTranslate('modules.badges.total-badges.counter.text', { badgesCount }),
    },
    addBadgeBtnTitle: useTranslate('modules.badges.button.add-badge'),
  };

  return (
    <header className="mt-4 mb-4">
      <Stack className="justify-content-between" direction={isExtraSmall ? 'vertical' : 'horizontal'}>
        <h1 className="mb-0">{messages.headingText}</h1>
        {!isError && (
          <Stack direction={isExtraSmall ? 'vertical' : 'horizontal'} gap={3}>
            <p className="m-0">
              {messages.totalBadges.counterText}
            </p>
            <Button onClick={openBadgeModalDialog}>
              {messages.addBadgeBtnTitle}
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
  openBadgeModalDialog: PropTypes.func.isRequired,
};

export default SubHeader;

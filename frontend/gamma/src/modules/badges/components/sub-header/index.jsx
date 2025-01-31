import React from 'react';
import {
  Button, Stack, useMediaQuery, breakpoints,
} from '@openedx/paragon';

import { useTranslate } from '../../../../i18n/utils';

const SubHeader = () => {
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  return (
    <header className="mt-4 mb-4">
      <Stack className="justify-content-between" direction={isExtraSmall ? 'vertical' : 'horizontal'}>
        <h1>{useTranslate('modules.badges.heading.text')}</h1>
        <Stack direction={isExtraSmall ? 'vertical' : 'horizontal'} gap={3}>
          <p className="m-0">
            {useTranslate('modules.badges.total-badges.counter.text', { badgesCount: 0 })}
          </p>
          <Button>{useTranslate('modules.badges.button.add-badge')}</Button>
        </Stack>
      </Stack>
    </header>
  );
};

export default SubHeader;

import React from 'react';
import { Container, Button } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';
import { SubHeader } from './components';

export const Badges = () => (
  <Container size="lg">
    <SubHeader />
    <Button block data-testid="add-badge-button">
      {useTranslate('modules.badges.button.add-badge')}
    </Button>
  </Container>
);

import React from 'react';
import { Container, Button } from '@openedx/paragon';
import { useIntl } from 'react-intl';

import {
  SEOHelmet, Header, Footer, SubHeader,
} from '../../generic';
import { AvatarList } from './components';
import moduleMessages from './i18n';

import './assets/scss/index.scss';

export const Avatars = () => {
  const intl = useIntl();

  return (
    <>
      <Header />
      <main className="mt-4 mb-4 flex-grow-1">
        <SEOHelmet
          title={intl.formatMessage(moduleMessages.pageTitle)}
          description={intl.formatMessage(moduleMessages.pageDescription)}
        />
        <Container size="lg">
          <SubHeader
            isError={false}
            title={intl.formatMessage(moduleMessages.pageTitle)}
            btnTitle={intl.formatMessage(moduleMessages.addAvatarBtnText)}
            description={intl.formatMessage(moduleMessages.totalAvatarsCount, { avatarsCount: 0 })}
            onClick={() => {}}
          />
          <AvatarList />
          <Button
            block
            data-testid="add-avatar-button"
          >
            {intl.formatMessage(moduleMessages.addAvatarBtnText)}
          </Button>
        </Container>
      </main>
      <Footer />
    </>
  );
};

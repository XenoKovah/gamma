import React, { useState } from 'react';
import { Container, Button } from '@openedx/paragon';

import { AlertComponent, Loader, SEOHelmet } from '../../generic';
import { useTranslate } from '../../i18n/utils';
import { useBadgesData } from './data';
import { BadgesList, SubHeader } from './components';

import './assets/scss/index.scss';

export const Badges = () => {
  const { data: badgesData, isLoading, isError } = useBadgesData();
  const [showErrorAlert, setShowErrorAlert] = useState(false);

  const messages = {
    pageTitle: useTranslate('modules.badges.heading.text'),
    pageDescription: useTranslate('modules.badges.page.description'),
    addBadgeBtnText: useTranslate('modules.badges.button.add-badge'),
    alert: {
      error: {
        title: useTranslate('generic.alert.danger.title'),
        description: useTranslate('generic.alert.danger.description'),
      },
    },
  };

  if (isLoading) {
    return <Loader />;
  }

  return (
    <main className="mt-4 mb-4">
      <SEOHelmet
        title={messages.pageTitle}
        description={messages.pageDescription}
      />
      <Container size="lg">
        <SubHeader isError={isError} badgesCount={badgesData.length} />
        {isError && !showErrorAlert && (
          <AlertComponent
            title={messages.alert.error.title}
            description={messages.alert.error.description}
            variant="danger"
            onClose={() => setShowErrorAlert(!showErrorAlert)}
            isDismissible
          />
        )}
        {!isError && (
          <>
            <BadgesList badgesData={badgesData} />
            <Button block data-testid="add-badge-button">
              {messages.addBadgeBtnText}
            </Button>
          </>
        )}
      </Container>
    </main>
  );
};

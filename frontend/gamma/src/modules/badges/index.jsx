import React, { useState } from 'react';
import { Container, Button, useToggle } from '@openedx/paragon';

import {
  AlertComponent, Loader, SEOHelmet, AlertModal,
} from '../../generic';
import { useTranslate } from '../../i18n/utils';
import { useBadgesData } from './data';
import { BadgesList, BadgeModal, SubHeader } from './components';

import './assets/scss/index.scss';

export const Badges = () => {
  const { data: badgesData, isLoading, isError } = useBadgesData();
  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [isOpenModalDialog, openModalDialog, closeModalDialog] = useToggle(false);
  const [isOpen, open, close] = useToggle(false);

  const messages = {
    pageTitle: useTranslate('modules.badges.heading.text'),
    pageDescription: useTranslate('modules.badges.page.description'),
    addBadgeBtnText: useTranslate('modules.badges.button.add-badge'),
    alert: {
      error: {
        title: useTranslate('generic.alert.danger.title'),
        description: useTranslate('generic.alert.danger.description'),
      },
      confirmDeletionModal: {
        title: useTranslate('modules.badges.alert.modal.confirm.deletion.title'),
        description: useTranslate('modules.badges.alert.modal.confirm.deletion.description'),
      },
    },
  };

  if (isLoading) {
    return <Loader />;
  }

  return (
    <main className="mt-4 mb-4">
      <AlertModal
        title={messages.alert.confirmDeletionModal.title}
        isOpen={isOpen}
        onClose={close}
        onDelete={() => {}}
        description={messages.alert.confirmDeletionModal.description}
      />
      <BadgeModal
        isOpenModalDialog={isOpenModalDialog}
        closeModalDialog={closeModalDialog}
      />
      <SEOHelmet
        title={messages.pageTitle}
        description={messages.pageDescription}
      />
      <Container size="lg">
        <SubHeader
          isError={isError}
          badgesCount={badgesData?.length}
          openBadgeModalDialog={openModalDialog}
        />
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
            <BadgesList badgesData={badgesData} openConfirmDeletionAlert={open} />
            <Button block data-testid="add-badge-button" onClick={openModalDialog}>
              {messages.addBadgeBtnText}
            </Button>
          </>
        )}
      </Container>
    </main>
  );
};

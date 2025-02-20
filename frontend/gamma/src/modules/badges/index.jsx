import React from 'react';
import { Container, Button } from '@openedx/paragon';

import {
  AlertComponent, Loader, SEOHelmet, ManageEntityModal,
  AlertModal, Header, Footer, ToastComponent,
} from '../../generic';
import { useTranslate } from '../../i18n/utils';
import { useCoursesData, useOrganizationsData } from './data';
import { BadgesList, SubHeader } from './components';
import { useBadges } from './hooks/useBadges';

import './assets/scss/index.scss';

export const Badges = () => {
  const {
    isError,
    isLoading,
    badgesData,
    actionsData,
    coursesData,
    firstBadgeRef,
    submitStatus,
    showErrorAlert,
    showErrorToast,
    deletionStatus,
    setSubmitStatus,
    setShowErrorToast,
    setShowErrorAlert,
    organizationsData,
    handleCreateNewBadge,
    openManageEntityModal,
    showBadgeCreatedAlert,
    handleDeleteBadgeById,
    closeManageEntityModal,
    isManageEntityModalOpen,
    openConfirmDeletionAlert,
    closeDeletionManageEntityModal,
    isDeletionManageEntityModalOpen,
  } = useBadges();

  const messages = {
    pageTitle: useTranslate('modules.badges.heading.text'),
    addManageEntityModalTitle: useTranslate('modules.badges.modal.add-badge.title'),
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
      badgeCreated: {
        title: useTranslate('modules.badges.alert.badge-created.title'),
        description: useTranslate('modules.badges.alert.badge-created.description'),
      },
    },
    toast: {
      error: useTranslate('modules.badges.toast.error.text'),
    },
  };

  if (isLoading) {
    return <Loader />;
  }

  const successAlert = showBadgeCreatedAlert && {
    title: messages.alert.badgeCreated.title,
    description: messages.alert.badgeCreated.description,
    variant: 'success',
  };

  const errorAlert = (isError || showErrorAlert) && {
    title: messages.alert.error.title,
    description: messages.alert.error.description,
    variant: 'danger',
    onClose: () => setShowErrorAlert(!showErrorAlert),
    isDismissible: true,
  };

  const alertProps = successAlert || errorAlert || null;

  return (
    <>
      <Header />
      <main className="my-4 flex-grow-1">
        <AlertModal
          title={messages.alert.confirmDeletionModal.title}
          isOpen={isDeletionManageEntityModalOpen}
          onClose={closeDeletionManageEntityModal}
          onDelete={handleDeleteBadgeById}
          description={messages.alert.confirmDeletionModal.description}
          isStatefulButton
          submitStatus={deletionStatus}
        />
        <ManageEntityModal
          isManageEntityModalOpen={isManageEntityModalOpen}
          useCoursesData={useCoursesData}
          title={messages.addManageEntityModalTitle}
          useOrganizationsData={useOrganizationsData}
          data={{
            courses: coursesData?.courses || [],
            organizations: organizationsData?.organisations || [],
            actions: actionsData || [],
          }}
          submitForm={handleCreateNewBadge}
          submitStatus={submitStatus}
          setSubmitStatus={setSubmitStatus}
          onReset={closeManageEntityModal}
        />
        <SEOHelmet
          title={messages.pageTitle}
          description={messages.pageDescription}
        />
        <Container size="lg">
          <SubHeader
            isError={isError}
            badgesCount={badgesData?.length}
            openManageEntityModal={openManageEntityModal}
          />
          {alertProps && <AlertComponent {...alertProps} />}
          {showErrorToast && (
            <ToastComponent
              text={messages.toast.error}
              onClose={() => setShowErrorToast(!showErrorToast)}
            />
          )}
          {!isError && (
            <>
              <BadgesList
                badgesData={badgesData}
                openConfirmDeletionAlert={openConfirmDeletionAlert}
                firstBadgeRef={firstBadgeRef}
              />
              <Button
                block
                data-testid="add-badge-button"
                onClick={openManageEntityModal}
              >
                {messages.addBadgeBtnText}
              </Button>
            </>
          )}
        </Container>
      </main>
      <Footer />
    </>
  );
};

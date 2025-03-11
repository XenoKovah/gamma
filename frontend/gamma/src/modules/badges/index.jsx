import React from 'react';
import { Container, Button } from '@openedx/paragon';
import { useIntl } from 'react-intl';

import {
  AlertComponent, Loader, SEOHelmet, ManageEntityModal,
  AlertModal, Header, Footer, ToastComponent, SubHeader,
} from '../../generic';
import genericMessages from '../../i18n';
import { BadgesList } from './components';
import { useBadges } from './hooks/useBadges';
import moduleMessages from './i18n';

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
  const intl = useIntl();

  if (isLoading) {
    return <Loader />;
  }

  const successAlert = showBadgeCreatedAlert && {
    title: intl.formatMessage(moduleMessages.badgeCreatedTitle),
    description: intl.formatMessage(moduleMessages.badgeCreatedDescription),
    variant: 'success',
  };

  const errorAlert = (isError || showErrorAlert) && {
    title: intl.formatMessage(genericMessages.alertDangerTitle),
    description: intl.formatMessage(genericMessages.alertDangerDescription),
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
          title={intl.formatMessage(moduleMessages.confirmDeletionModalTitle)}
          isOpen={isDeletionManageEntityModalOpen}
          onClose={closeDeletionManageEntityModal}
          onDelete={handleDeleteBadgeById}
          description={intl.formatMessage(moduleMessages.confirmDeletionModalDescription)}
          isStatefulButton
          submitStatus={deletionStatus}
        />
        <ManageEntityModal
          isManageEntityModalOpen={isManageEntityModalOpen}
          title={intl.formatMessage(moduleMessages.addManageEntityModalTitle)}
          data={{
            courses: coursesData?.courses || [],
            organizations: organizationsData?.organizations || [],
            actions: actionsData || [],
          }}
          submitForm={handleCreateNewBadge}
          submitStatus={submitStatus}
          setSubmitStatus={setSubmitStatus}
          onReset={closeManageEntityModal}
        />
        <SEOHelmet
          title={intl.formatMessage(moduleMessages.pageTitle)}
          description={intl.formatMessage(moduleMessages.pageDescription)}
        />
        <Container size="lg">
          <SubHeader
            isError={isError}
            title={intl.formatMessage(moduleMessages.pageTitle)}
            btnTitle={intl.formatMessage(moduleMessages.addBadgeBtnText)}
            description={intl.formatMessage(moduleMessages.totalBadgesCount, { badgesCount: badgesData?.length || 0 })}
            onClick={openManageEntityModal}
          />
          {alertProps && <AlertComponent {...alertProps} />}
          {showErrorToast && (
            <ToastComponent
              text={intl.formatMessage(moduleMessages.toastErrorTitle)}
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
                {intl.formatMessage(moduleMessages.addBadgeBtnText)}
              </Button>
            </>
          )}
        </Container>
      </main>
      <Footer />
    </>
  );
};

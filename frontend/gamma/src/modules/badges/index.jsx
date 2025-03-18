import React from 'react';
import { Container, Button } from '@openedx/paragon';
import { useIntl } from 'react-intl';

import {
  AlertComponent, Loader, SEOHelmet, ManageEntityModal,
  AlertModal, Header, Footer, ToastComponent, SubHeader,
} from '../../generic';
import genericMessages from '../../i18n';
import { BadgesList } from './components';
import { TOAST_TYPES } from './constants';
import { useBadges } from './hooks/useBadges';
import moduleMessages from './i18n';

import './assets/scss/index.scss';

export const Badges = () => {
  const {
    toast,
    isError,
    showToast,
    isLoading,
    badgesData,
    actionsData,
    coursesData,
    submitStatus,
    firstBadgeRef,
    showErrorAlert,
    deletionStatus,
    editedBadgeData,
    handleEditBadge,
    setSubmitStatus,
    setShowErrorAlert,
    organizationsData,
    setEditedBadgeData,
    handleCreateNewBadge,
    openManageEntityModal,
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

  const getNotificationToastProps = () => {
    if (!toast) { return null; }

    const toastMessages = {
      [TOAST_TYPES.BADGE.CREATED]: {
        isShow: true,
        text: intl.formatMessage(moduleMessages.badgeCreatedTitle),
        variant: 'success',
        onClose: () => showToast(null),
      },
      [TOAST_TYPES.BADGE.EDITED]: {
        isShow: true,
        text: intl.formatMessage(moduleMessages.badgeEditedTitle),
        variant: 'success',
        onClose: () => showToast(null),
      },
      [TOAST_TYPES.BADGE.DELETED]: {
        isShow: true,
        text: intl.formatMessage(moduleMessages.badgeDeletedTitle),
        variant: 'success',
        onClose: () => showToast(null),
      },
      [TOAST_TYPES.ERROR]: {
        isShow: true,
        text: intl.formatMessage(moduleMessages.toastErrorTitle),
        variant: 'danger',
        onClose: () => showToast(null),
      },
    };

    return toastMessages[toast] || null;
  };

  const handleOpenManageEntityModal = (badgeId) => {
    openManageEntityModal();
    const badge = badgesData.find((badgeItem) => badgeItem.id === badgeId);
    setEditedBadgeData(badge);
  };

  const handleResetManageEntityModal = () => {
    closeManageEntityModal();
    setEditedBadgeData(null);
  };

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
            entityData: editedBadgeData,
            courses: coursesData?.courses || [],
            organizations: organizationsData?.organizations || [],
            actions: actionsData || [],
          }}
          submitForm={editedBadgeData ? handleEditBadge : handleCreateNewBadge}
          submitStatus={submitStatus}
          setSubmitStatus={setSubmitStatus}
          onReset={handleResetManageEntityModal}
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
          {isError && (
            <AlertComponent
              variant="danger"
              title={intl.formatMessage(genericMessages.alertDangerTitle)}
              description={intl.formatMessage(genericMessages.alertDangerDescription)}
              onClose={() => setShowErrorAlert(!showErrorAlert)}
              isDismissible
            />
          )}
          {getNotificationToastProps() && <ToastComponent {...getNotificationToastProps()} />}
          {!isError && (
            <>
              <BadgesList
                badgesData={badgesData}
                openConfirmDeletionAlert={openConfirmDeletionAlert}
                firstBadgeRef={firstBadgeRef}
                handleOpenManageEntityModal={handleOpenManageEntityModal}
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

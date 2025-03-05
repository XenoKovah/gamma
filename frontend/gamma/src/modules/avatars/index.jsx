import React, { useEffect } from 'react';
import { useIntl } from 'react-intl';
import { Button, Container } from '@openedx/paragon';

import {
  AlertComponent,
  AlertModal,
  Footer,
  Header,
  Loader,
  SEOHelmet,
  SubHeader,
  ToastComponent,
} from '../../generic';

import { useAvatarSets } from './hooks/useAvatarSets';
import { AvatarSetList, AvatarSetStepper } from './components';

import genericMessages from '../../i18n';
import moduleMessages from './i18n';

import './assets/scss/index.scss';

export const Avatars = () => {
  const intl = useIntl();

  const {
    activeToast,
    submitStatus,
    deletionStatus,
    showErrorAlert,
    avatarSetsData,
    setShowErrorAlert,
    isAvatarSetsDataError,
    isAvatarSetsDataLoading,
    openConfirmDeletionModal,
    handleCreateNewAvatarSet,
    openManageAvatarSetModal,
    handleDeleteAvatarSetById,
    closeManageAvatarSetModal,
    isManageAvatarSetModalOpen,
    closeDeletionAvatarSetModal,
    isDeletionAvatarSetModalOpen,
    handleUpdateAvatarSet,
  } = useAvatarSets();

  useEffect(() => {
    if (showErrorAlert || isAvatarSetsDataError) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [showErrorAlert, isAvatarSetsDataError]);

  if (isAvatarSetsDataLoading) {
    return <Loader />;
  }

  const errorAlert = (isAvatarSetsDataError || showErrorAlert) && {
    title: intl.formatMessage(genericMessages.alertDangerTitle),
    description: intl.formatMessage(genericMessages.alertDangerDescription),
    variant: 'danger',
    onClose: () => setShowErrorAlert(!showErrorAlert),
    isDismissible: true,
  };

  const alertProps = errorAlert || null;

  return (
    <>
      <Header />
      <main className="avatars-settings mt-4 mb-4 flex-grow-1">
        <SEOHelmet
          title={intl.formatMessage(moduleMessages.pageTitle)}
          description={intl.formatMessage(moduleMessages.pageDescription)}
        />
        <AvatarSetStepper
          isManageAvatarSetModalOpen={isManageAvatarSetModalOpen}
          closeManageAvatarSetModal={closeManageAvatarSetModal}
          handleCreateNewAvatarSet={handleCreateNewAvatarSet}
          submitStatus={submitStatus}
          avatarSetsData={avatarSetsData}
          handleUpdateAvatarSet={handleUpdateAvatarSet}
        />
        <AlertModal
          title={intl.formatMessage(moduleMessages.confirmDeletionModalTitle)}
          isOpen={isDeletionAvatarSetModalOpen}
          onClose={closeDeletionAvatarSetModal}
          onDelete={handleDeleteAvatarSetById}
          description={intl.formatMessage(moduleMessages.confirmDeletionModalDescription)}
          isStatefulButton
          submitStatus={deletionStatus}
        />
        <Container size="lg">
          <SubHeader
            isError={isAvatarSetsDataError}
            title={intl.formatMessage(moduleMessages.pageTitle)}
            btnTitle={intl.formatMessage(moduleMessages.addAvatarSetBtnText)}
            description={
              intl.formatMessage(moduleMessages.totalAvatarSetsCount, { avatarSetsCount: avatarSetsData?.length || 0 })
            }
            onClick={openManageAvatarSetModal}
          />
          {alertProps && <AlertComponent {...alertProps} />}
          {activeToast && (
            <ToastComponent
              className={isManageAvatarSetModalOpen ? 'avatars-settings-toast' : ''}
              variant={activeToast.variant}
              text={activeToast.text}
              isShow
              onClose={activeToast.onClose}
              delay={1000}
            />
          )}
          {!isAvatarSetsDataError && (
            <>
              <AvatarSetList
                avatarSetsData={avatarSetsData}
                openConfirmDeletionModal={openConfirmDeletionModal}
              />
              <Button
                block
                data-testid="add-avatar-set-button"
                onClick={openManageAvatarSetModal}
              >
                {intl.formatMessage(moduleMessages.addAvatarSetBtnText)}
              </Button>
            </>
          )}
        </Container>
      </main>
      <Footer />
    </>
  );
};

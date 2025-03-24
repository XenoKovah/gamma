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
import { DEFAULT_DELAY } from './constants';

import genericMessages from '../../i18n';
import moduleMessages from './i18n';

import './assets/scss/index.scss';

export const Avatars = () => {
  const intl = useIntl();

  const {
    isError,
    isLoading,
    coursesData,
    actionsData,
    activeToast,
    submitStatus,
    deletionStatus,
    showErrorAlert,
    avatarSetsData,
    setSubmitStatus,
    setShowErrorAlert,
    organizationsData,
    handleDeleteAvatar,
    handleUpdateAvatar,
    handleUpdateAvatarSet,
    handleFinishAvatarSet,
    isEditStepperMode,
    setIsEditStepperMode,
    openConfirmDeletionModal,
    handleCreateNewAvatarSet,
    openManageAvatarSetModal,
    handleDeleteAvatarSetById,
    closeManageAvatarSetModal,
    isManageAvatarSetModalOpen,
    closeDeletionAvatarSetModal,
    isDeletionAvatarSetModalOpen,
  } = useAvatarSets();

  const avatarSetStepperTitle = isEditStepperMode
    ? intl.formatMessage(moduleMessages.avatarSetStepperEditTitle)
    : intl.formatMessage(moduleMessages.avatarSetStepperTitle);

  useEffect(() => {
    if (showErrorAlert || isError) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [showErrorAlert, isError]);

  if (isLoading) {
    return <Loader />;
  }

  const errorAlert = (isError || showErrorAlert) && {
    title: intl.formatMessage(genericMessages.alertDangerTitle),
    description: intl.formatMessage(genericMessages.alertDangerDescription),
    variant: 'danger',
    onClose: () => setShowErrorAlert(!showErrorAlert),
    isDismissible: true,
  };

  const alertProps = errorAlert || null;

  const handleOpenManageAvatarSetModal = () => {
    openManageAvatarSetModal();
    setIsEditStepperMode(false);
  };

  return (
    <>
      <Header />
      <main className="avatars-settings my-4 flex-grow-1">
        <SEOHelmet
          title={intl.formatMessage(moduleMessages.pageTitle)}
          description={intl.formatMessage(moduleMessages.pageDescription)}
        />
        <AvatarSetStepper
          avatarSetStepperTitle={avatarSetStepperTitle}
          isManageAvatarSetModalOpen={isManageAvatarSetModalOpen}
          closeManageAvatarSetModal={closeManageAvatarSetModal}
          handleCreateNewAvatarSet={handleCreateNewAvatarSet}
          submitStatus={submitStatus}
          avatarSetsData={avatarSetsData}
          handleUpdateAvatarSet={handleUpdateAvatarSet}
          handleDeleteAvatar={handleDeleteAvatar}
          deletionStatus={deletionStatus}
          setSubmitStatus={setSubmitStatus}
          coursesData={coursesData}
          organizationsData={organizationsData}
          actionsData={actionsData}
          handleUpdateAvatar={handleUpdateAvatar}
          handleFinishAvatarSet={handleFinishAvatarSet}
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
            isError={isError}
            title={intl.formatMessage(moduleMessages.pageTitle)}
            btnTitle={intl.formatMessage(moduleMessages.addAvatarSetBtnText)}
            description={
              intl.formatMessage(
                moduleMessages.totalAvatarSetsCount,
                { avatarSetsCount: avatarSetsData?.length || 0 },
              )
            }
            onClick={handleOpenManageAvatarSetModal}
          />
          {alertProps && <AlertComponent {...alertProps} />}
          {activeToast && (
            <ToastComponent
              className={isManageAvatarSetModalOpen ? 'avatars-settings-toast' : ''}
              variant={activeToast.variant}
              text={activeToast.text}
              isShow
              onClose={activeToast.onClose}
              delay={DEFAULT_DELAY}
            />
          )}
          {!isError && (
            <>
              <AvatarSetList
                avatarSetsData={avatarSetsData}
                openConfirmDeletionModal={openConfirmDeletionModal}
                openManageAvatarSetModal={openManageAvatarSetModal}
                setIsEditStepperMode={setIsEditStepperMode}
              />
              <Button
                block
                data-testid="add-avatar-set-button"
                onClick={handleOpenManageAvatarSetModal}
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

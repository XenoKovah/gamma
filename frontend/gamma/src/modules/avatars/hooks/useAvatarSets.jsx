import {
  useEffect, useReducer, useState, useCallback, useMemo,
} from 'react';
import { useIntl } from 'react-intl';
import { useMutation } from 'react-query';
import { useToggle } from '@openedx/paragon';

import { submitBtnStatuses } from '../../../generic';
import { useAvatarsContext } from '../context/AvatarsContext';
import { DEFAULT_DELAY, DELETION_STATES } from '../constants';
import {
  useCoursesData,
  useActionsData,
  deleteAvatarSet,
  createAvatarSet,
  updateAvatarSet,
  updateAvatarById,
  deleteAvatarById,
  useAvatarSetsData,
  useOrganizationsData,
  finishUpdatingAvatarSet,
} from '../data';
import { deletionReducer } from '../reducers';
import { setAutoClose } from '../utils';

import moduleMessages from '../i18n';

export const useAvatarSets = () => {
  const intl = useIntl();
  const {
    data: avatarSetsData,
    isLoading: isAvatarSetsDataLoading,
    isError: isAvatarSetsDataError,
    refetch: refetchAvatarSetsData,
  } = useAvatarSetsData();
  const {
    data: coursesData,
    isLoading: isCoursesDataLoading,
    isError: isCoursesDataError,
  } = useCoursesData();
  const {
    data: organizationsData,
    isLoading: isOrganizationsDataLoading,
    isError: isOrganizationsDataError,
  } = useOrganizationsData();
  const {
    data: actionsData,
    isLoading: isActionsDataLoading,
    isError: isActionsDataError,
  } = useActionsData();
  const { setCurrentAvatarSetData } = useAvatarsContext();

  const isLoading = isAvatarSetsDataLoading
    || isCoursesDataLoading || isOrganizationsDataLoading || isActionsDataLoading;
  const isError = isAvatarSetsDataError || isCoursesDataError || isOrganizationsDataError || isActionsDataError;

  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [deletingAvatarSetId, setDeletingAvatarSetId] = useState(null);
  const [submitStatus, setSubmitStatus] = useState(submitBtnStatuses.DEFAULT);
  const [showAvatarSetCreatedSuccessfully, setShowAvatarSetCreatedSuccessfully] = useState(false);
  const [showAvatarSetDeletedSuccessfully, setShowAvatarSetDeletedSuccessfully] = useState(false);

  const [
    isDeletionAvatarSetModalOpen, openDeletionAvatarSetModal, closeDeletionAvatarSetModal,
  ] = useToggle(false);
  const [
    isManageAvatarSetModalOpen, openManageAvatarSetModal, closeManageAvatarSetModal,
  ] = useToggle(false);
  const [deletionStatus, dispatchDeletionStatus] = useReducer(deletionReducer, DELETION_STATES.RESET);

  useEffect(() => showErrorAlert && setAutoClose(setShowErrorAlert, DEFAULT_DELAY), [showErrorAlert]);

  const activeToast = useMemo(() => {
    const toastConfigs = [
      {
        condition: showErrorToast,
        variant: 'danger',
        text: intl.formatMessage(moduleMessages.toastErrorTitle),
        onClose: () => setShowErrorToast(false),
      },
      {
        condition: showAvatarSetCreatedSuccessfully,
        variant: 'success',
        text: intl.formatMessage(moduleMessages.toastNewAvatarSetSavedSuccessfullyTitle),
        onClose: () => setShowAvatarSetCreatedSuccessfully(false),
      },
      {
        condition: showAvatarSetDeletedSuccessfully,
        variant: 'success',
        text: intl.formatMessage(moduleMessages.toastAvatarSetDeletedSuccessfullyTitle),
        onClose: () => setShowAvatarSetDeletedSuccessfully(false),
      },
    ];

    return toastConfigs.find((toast) => toast.condition) || null;
  }, [
    intl,
    showErrorToast,
    showAvatarSetCreatedSuccessfully,
    showAvatarSetDeletedSuccessfully,
  ]);

  const handleCloseAlertError = () => {
    closeDeletionAvatarSetModal();
    dispatchDeletionStatus({ type: DELETION_STATES.RESET });
  };

  const mutation = useMutation({
    mutationFn: deleteAvatarSet,
    onSuccess: () => {
      refetchAvatarSetsData();
      dispatchDeletionStatus({ type: DELETION_STATES.SUCCESS });
      handleCloseAlertError();
      setShowAvatarSetDeletedSuccessfully(true);
    },
    onError: () => {
      dispatchDeletionStatus({ type: DELETION_STATES.ERROR });
      setShowErrorToast(true);
      handleCloseAlertError();
      setShowAvatarSetDeletedSuccessfully(false);
    },
  });

  const handleDeleteAvatarSetById = () => {
    dispatchDeletionStatus({ type: DELETION_STATES.START });
    if (deletingAvatarSetId) {
      mutation.mutate(deletingAvatarSetId);
    }
  };

  const openConfirmDeletionModal = (id) => {
    setDeletingAvatarSetId(id);
    openDeletionAvatarSetModal();
  };

  const handleCreateNewAvatarSet = useCallback(async (values, callback) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      const avatarSet = await createAvatarSet(values);
      await refetchAvatarSetsData();
      setShowAvatarSetCreatedSuccessfully(true);
      setCurrentAvatarSetData(avatarSet);
      callback();
    } catch (error) {
      console.error('Error creating avatar set:', error); // eslint-disable-line no-console
      setShowErrorToast(true);
      setSubmitStatus(submitBtnStatuses.ERROR);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  }, [createAvatarSet]);

  const handleUpdateAvatarSet = async (avatarSetData, callback) => {
    setSubmitStatus(submitBtnStatuses.PENDING);

    try {
      await updateAvatarSet(avatarSetData);
      await refetchAvatarSetsData();
      setShowAvatarSetCreatedSuccessfully(true);
      callback();
    } catch (error) {
      console.error('Error updating avatar set:', error); // eslint-disable-line no-console
      setShowErrorToast(true);
      setSubmitStatus(submitBtnStatuses.ERROR);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  const handleDeleteAvatar = async (avatarId, callback) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await deleteAvatarById(avatarId);
      await refetchAvatarSetsData();
      handleCloseAlertError();
      setShowAvatarSetDeletedSuccessfully(true);
      dispatchDeletionStatus({ type: DELETION_STATES.SUCCESS });
      callback();
    } catch (error) {
      console.error('Error deleting avatar:', error); // eslint-disable-line no-console
      setSubmitStatus(submitBtnStatuses.ERROR);
      dispatchDeletionStatus({ type: DELETION_STATES.ERROR });
      setShowErrorToast(true);
      handleCloseAlertError();
      setShowAvatarSetDeletedSuccessfully(false);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  const handleUpdateAvatar = async (entityId, values, resetForm, handleReset) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await updateAvatarById(entityId, values);
      await refetchAvatarSetsData();
      setShowAvatarSetCreatedSuccessfully(true);
      handleReset(resetForm);
    } catch (error) {
      setShowErrorToast(true);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  const handleFinishAvatarSet = async (id, callbackFn) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await finishUpdatingAvatarSet(id);
      setShowAvatarSetCreatedSuccessfully(true);
      callbackFn();
    } catch (error) {
      setShowErrorToast(true);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  return {
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
    openConfirmDeletionModal,
    handleCreateNewAvatarSet,
    openManageAvatarSetModal,
    handleDeleteAvatarSetById,
    closeManageAvatarSetModal,
    isManageAvatarSetModalOpen,
    closeDeletionAvatarSetModal,
    isDeletionAvatarSetModalOpen,
  };
};

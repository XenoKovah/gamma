import {
  useEffect, useReducer, useState, useCallback, useMemo,
} from 'react';
import { useIntl } from 'react-intl';
import { useMutation } from 'react-query';
import { useToggle } from '@openedx/paragon';

import { submitBtnStatuses } from '../../../generic';
import { DEFAULT_DELAY, DELETION_STATES } from '../constants';
import { deleteAvatarSet, useAvatarSetsData, createAvatarSet } from '../data';
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
        text: intl.formatMessage(moduleMessages.toastNewAvatarSetCreatedSuccessfullyTitle),
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

  const handleCreateNewAvatarSet = useCallback(async (values) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await createAvatarSet(values);
      await refetchAvatarSetsData();
      setShowAvatarSetCreatedSuccessfully(true);
    } catch (error) {
      console.error('Error creating avatar set:', error); // eslint-disable-line no-console
      setShowErrorToast(true);
      setSubmitStatus(submitBtnStatuses.ERROR);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  }, [createAvatarSet]);

  return {
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
    showAvatarSetCreatedSuccessfully,
  };
};

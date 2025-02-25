import { useToggle } from '@openedx/paragon';
import { useEffect, useReducer, useState } from 'react';
import { useMutation } from 'react-query';

import { DEFAULT_DELAY, DELETION_STATES } from '../constants';
import { deleteAvatarSet, useAvatarSetsData } from '../data';
import { deletionReducer } from '../reducers';
import { setAutoClose } from '../utils';

export const useAvatarSets = () => {
  const {
    data: avatarSetsData,
    isLoading: isAvatarSetsDataLoading,
    isError: isAvatarSetsDataError,
    refetch: refetchAvatarSetsData,
  } = useAvatarSetsData();

  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [deletingAvatarSetId, setDeletingAvatarSetId] = useState(null);

  const [
    isDeletionAvatarSetModalOpen, openDeletionAvatarSetModal, closeDeletionAvatarSetModal,
  ] = useToggle(false);
  const [deletionStatus, dispatchDeletionStatus] = useReducer(deletionReducer, DELETION_STATES.RESET);

  useEffect(() => showErrorAlert && setAutoClose(setShowErrorAlert, DEFAULT_DELAY), [showErrorAlert]);

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
    },
    onError: () => {
      dispatchDeletionStatus({ type: DELETION_STATES.ERROR });
      setShowErrorAlert(true);
      handleCloseAlertError();
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

  return {
    deletionStatus,
    showErrorToast,
    showErrorAlert,
    avatarSetsData,
    setShowErrorToast,
    setShowErrorAlert,
    isAvatarSetsDataError,
    isAvatarSetsDataLoading,
    openConfirmDeletionModal,
    handleDeleteAvatarSetById,
    closeDeletionAvatarSetModal,
    isDeletionAvatarSetModalOpen,
  };
};

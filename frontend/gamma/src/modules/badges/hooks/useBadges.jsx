import {
  useState, useReducer, useRef, useEffect, useCallback,
} from 'react';
import { useToggle } from '@openedx/paragon';
import { useMutation } from 'react-query';

import { submitBtnStatuses } from '../../../generic';
import {
  deleteBadge, useBadgesData, createBadge, useCoursesData,
  useOrganizationsData, useActionsData,
} from '../data';
import { DELETION_STATES, DEFAULT_DELAY } from '../constants';
import { deletionReducer } from '../reducers';
import { setAutoClose } from '../utils';

export const useBadges = () => {
  const {
    data: badgesData,
    isLoading: isBadgesDataLoading,
    isError: isBadgesDataError,
    refetch: refetchBadgesData,
  } = useBadgesData();
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

  const isLoading = isBadgesDataLoading || isCoursesDataLoading || isOrganizationsDataLoading || isActionsDataLoading;
  const isError = isBadgesDataError || isCoursesDataError || isOrganizationsDataError || isActionsDataError;

  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [showBadgeCreatedAlert, setShowBadgeCreatedAlert] = useState(false);
  const [showErrorToast, setShowErrorToast] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(submitBtnStatuses.DEFAULT);

  const [isManageEntityModalOpen, openManageEntityModal, closeManageEntityModal] = useToggle(false);
  const [
    isDeletionManageEntityModalOpen, openDeletionManageEntityModal, closeDeletionManageEntityModal,
  ] = useToggle(false);
  const [deletionStatus, dispatchDeletionStatus] = useReducer(deletionReducer, DELETION_STATES.RESET);

  const [deletingBadgeId, setDeletingBadgeId] = useState(null);

  const firstBadgeRef = useRef(null);

  useEffect(() => showBadgeCreatedAlert
    && setAutoClose(setShowBadgeCreatedAlert, DEFAULT_DELAY), [showBadgeCreatedAlert]);
  useEffect(() => showErrorAlert && setAutoClose(setShowErrorAlert, DEFAULT_DELAY), [showErrorAlert]);

  useEffect(() => {
    if (firstBadgeRef.current && showBadgeCreatedAlert) {
      requestAnimationFrame(() => {
        firstBadgeRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    }
  }, [showBadgeCreatedAlert]);

  const handleCreateNewBadge = useCallback(async (values, resetForm, handleReset) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await createBadge(values);
      await refetchBadgesData();
      setShowBadgeCreatedAlert(true);
      handleReset(resetForm);
    } catch (error) {
      setShowErrorToast(true);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  }, [createBadge, refetchBadgesData, setShowBadgeCreatedAlert, setShowErrorToast]);

  const handleCloseAlertError = () => {
    closeDeletionManageEntityModal();
    dispatchDeletionStatus({ type: DELETION_STATES.RESET });
  };

  const mutation = useMutation({
    mutationFn: deleteBadge,
    onSuccess: () => {
      refetchBadgesData();
      dispatchDeletionStatus({ type: DELETION_STATES.SUCCESS });
      handleCloseAlertError();
    },
    onError: () => {
      dispatchDeletionStatus({ type: DELETION_STATES.ERROR });
      setShowErrorAlert(true);
      handleCloseAlertError();
    },
  });

  const handleDeleteBadgeById = () => {
    dispatchDeletionStatus({ type: DELETION_STATES.START });
    if (deletingBadgeId) {
      mutation.mutate(deletingBadgeId);
    }
  };

  const openConfirmDeletionAlert = (id) => {
    setDeletingBadgeId(id);
    openDeletionManageEntityModal();
  };

  return {
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
  };
};

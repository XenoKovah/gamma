import {
  useState, useReducer, useRef, useEffect,
} from 'react';
import { useToggle } from '@openedx/paragon';

import { submitBtnStatuses } from '../../../generic';
import {
  deleteBadge, useBadgesData, createBadge, useCoursesData,
  useOrganizationsData, useActionsData, editBadge, assignBadge,
} from '../data';
import { DELETION_STATES, DEFAULT_DELAY, TOAST_TYPES } from '../constants';
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

  const [toast, setToast] = useState(null);
  const [showErrorAlert, setShowErrorAlert] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(submitBtnStatuses.DEFAULT);
  const [editedBadgeData, setEditedBadgeData] = useState(null);
  const [deletingBadgeId, setDeletingBadgeId] = useState(null);
  const firstBadgeRef = useRef(null);
  const [isEditManageEntityModal, setIsEditManageEntityModal] = useState(false);

  const [isManageEntityModalOpen, openManageEntityModal, closeManageEntityModal] = useToggle(false);
  const [
    isDeletionManageEntityModalOpen, openDeletionManageEntityModal, closeDeletionManageEntityModal,
  ] = useToggle(false);
  const [deletionStatus, dispatchDeletionStatus] = useReducer(deletionReducer, DELETION_STATES.RESET);

  const [isAssignModalOpen, openAssignModal, closeAssignModal] = useToggle(false);
  const [assigningBadge, setAssigningBadge] = useState(null);
  const [isAssigning, setIsAssigning] = useState(false);
  const [assignResult, setAssignResult] = useState({ granted: 0, already: 0 });

  useEffect(() => {
    if (showErrorAlert) {
      setAutoClose(setShowErrorAlert, DEFAULT_DELAY);
    }
  }, [showErrorAlert]);

  const showToast = (type) => {
    setToast(type);
    setAutoClose(() => setToast(null), DEFAULT_DELAY);
  };

  const handleCreateNewBadge = async (values, resetForm, handleReset) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await createBadge(values);
      await refetchBadgesData();
      showToast(TOAST_TYPES.BADGE.CREATED);
      handleReset(resetForm);

      requestAnimationFrame(() => {
        if (firstBadgeRef.current) {
          firstBadgeRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    } catch (error) {
      showToast(TOAST_TYPES.ERROR);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  const handleEditBadge = async (badgeId, values, resetForm, handleReset) => {
    setSubmitStatus(submitBtnStatuses.PENDING);
    try {
      await editBadge(badgeId, values);
      await refetchBadgesData();
      showToast(TOAST_TYPES.BADGE.EDITED);
      handleReset(resetForm);
    } catch (error) {
      showToast(TOAST_TYPES.ERROR);
    } finally {
      setSubmitStatus(submitBtnStatuses.DEFAULT);
    }
  };

  const handleCloseAlertError = () => {
    closeDeletionManageEntityModal();
    dispatchDeletionStatus({ type: DELETION_STATES.RESET });
  };

  const handleDeleteBadgeById = async () => {
    dispatchDeletionStatus({ type: DELETION_STATES.START });

    if (!deletingBadgeId) {
      return;
    }

    try {
      await deleteBadge(deletingBadgeId);
      await refetchBadgesData();
      dispatchDeletionStatus({ type: DELETION_STATES.SUCCESS });
      showToast(TOAST_TYPES.BADGE.DELETED);
    } catch (error) {
      dispatchDeletionStatus({ type: DELETION_STATES.ERROR });
      showToast(TOAST_TYPES.ERROR);
    } finally {
      handleCloseAlertError();
    }
  };

  const openConfirmDeletionAlert = (id) => {
    setDeletingBadgeId(id);
    openDeletionManageEntityModal();
  };

  const handleOpenAssignModal = (badgeId) => {
    const badge = badgesData?.find((badgeItem) => badgeItem.id === badgeId) || null;
    setAssigningBadge(badge);
    openAssignModal();
  };

  const handleCloseAssignModal = () => {
    closeAssignModal();
    setAssigningBadge(null);
  };

  const handleAssignBadge = async (badgeId, userUids) => {
    setIsAssigning(true);
    try {
      const result = await assignBadge(badgeId, userUids);
      setAssignResult({
        granted: result?.granted?.length || 0,
        already: result?.already_assigned?.length || 0,
      });
      // Refresh so any points-derived data stays consistent after granting.
      await refetchBadgesData();
      showToast(TOAST_TYPES.BADGE.ASSIGNED);
      handleCloseAssignModal();
    } catch (error) {
      showToast(TOAST_TYPES.ERROR);
    } finally {
      setIsAssigning(false);
    }
  };

  return {
    toast,
    isError,
    showToast,
    isLoading,
    badgesData,
    actionsData,
    coursesData,
    submitStatus,
    isEditManageEntityModal,
    setIsEditManageEntityModal,
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
    isAssignModalOpen,
    assigningBadge,
    isAssigning,
    assignResult,
    handleOpenAssignModal,
    handleCloseAssignModal,
    handleAssignBadge,
  };
};

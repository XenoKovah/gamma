import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.badges.heading.text',
    defaultMessage: 'Badges settings',
    description: 'The text displayed in the heading of the badges settings page.',
  },
  pageDescription: {
    id: 'modules.badges.page.description',
    defaultMessage: 'This page displays badges and allows users to create and edit them.',
    description: 'The description for the badges settings page.',
  },
  addBadgeBtnText: {
    id: 'modules.badges.button.add-badge',
    defaultMessage: 'Add badge',
    description: 'The text displayed on the button to add a badge.',
  },
  totalBadgesCount: {
    id: 'modules.badges.total-badges.counter.text',
    defaultMessage: 'Total badges: {badgesCount}',
    description: 'The text displayed for the total number of badges.',
  },
  badgeEditBtnTitle: {
    id: 'modules.badges.badge-item.button.edit.title',
    defaultMessage: 'Edit',
    description: 'The text displayed on the button to edit a badge.',
  },
  badgeDeleteBtnTitle: {
    id: 'modules.badges.badge-item.button.delete.title',
    defaultMessage: 'Delete',
    description: 'The text displayed on the button to delete a badge.',
  },
  badgeAssignBtnTitle: {
    id: 'modules.badges.badge-item.button.assign.title',
    defaultMessage: 'Assign to users',
    description: 'The text on the button that opens the manual badge assignment modal.',
  },
  badgeUnassignBtnTitle: {
    id: 'modules.badges.badge-item.button.unassign.title',
    defaultMessage: 'Remove from users',
    description: 'The text on the button that opens the manual badge removal modal.',
  },
  badgeDefaultTitle: {
    id: 'modules.badges.badge-item.default.title',
    defaultMessage: 'Badge title',
    description: 'The default title for a badge.',
  },
  badgeDefaultDescription: {
    id: 'modules.badges.badge-item.default.description',
    defaultMessage: 'Badge description',
    description: 'The default description for a badge.',
  },
  alertEmptyBadgesListTitle: {
    id: 'modules.badges.alert.empty-badges-list.title',
    defaultMessage: 'No badges available',
    description: 'The title for the alert when there are no badges to display.',
  },
  alertEmptyBadgesListDescription: {
    id: 'modules.badges.alert.empty-badges-list.description',
    defaultMessage: 'There are currently no badges to display.',
    description: 'The description for the alert when there are no badges to display.',
  },
  addManageEntityModalTitle: {
    id: 'modules.badges.modal.add-badge.title',
    defaultMessage: 'Add new badge',
    description: 'The title for the badge modal.',
  },
  editManageEntityModalTitle: {
    id: 'modules.badges.modal.edit-badge.title',
    defaultMessage: 'Edit badge',
    description: 'The title for the edit badge modal.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.badges.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirm deletion',
    description: 'The title for the confirmation modal when deleting a badge.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.badges.alert.modal.confirm.deletion.description',
    defaultMessage: 'Are you sure you want to delete this badge? This action cannot be undone.',
    description: 'The description for the confirmation modal when deleting a badge.',
  },
  assignBadgeModalTitle: {
    id: 'modules.badges.modal.assign-badge.title',
    defaultMessage: 'Assign "{title}" to users',
    description: 'The title of the manual badge assignment modal.',
  },
  assignBadgeModalDescription: {
    id: 'modules.badges.modal.assign-badge.description',
    defaultMessage: 'Enter the user IDs (usernames) to grant this badge to, one per line or separated by commas.',
    description: 'Instructions shown in the manual badge assignment modal.',
  },
  assignBadgeModalPointsNote: {
    id: 'modules.badges.modal.assign-badge.points-note',
    defaultMessage: 'Each user will also receive {points} points.',
    description: 'Note shown when the badge being assigned awards points.',
  },
  assignBadgeModalUserIdsLabel: {
    id: 'modules.badges.modal.assign-badge.user-ids.label',
    defaultMessage: 'User IDs',
    description: 'Label for the user IDs textarea in the manual badge assignment modal.',
  },
  assignBadgeModalUserIdsPlaceholder: {
    id: 'modules.badges.modal.assign-badge.user-ids.placeholder',
    defaultMessage: 'e.g. jdoe, asmith\nor one user ID per line',
    description: 'Placeholder for the user IDs textarea in the manual badge assignment modal.',
  },
  assignBadgeModalSubmitBtnText: {
    id: 'modules.badges.modal.assign-badge.button.submit',
    defaultMessage: 'Assign badge',
    description: 'The submit button text in the manual badge assignment modal.',
  },
  assignBadgeModalSelectedCount: {
    id: 'modules.badges.modal.assign-badge.selected-count',
    defaultMessage: '{count, plural, one {# user} other {# users}} will be assigned this badge.',
    description: 'Shows how many distinct user IDs were entered in the assignment modal.',
  },
  unassignBadgeModalTitle: {
    id: 'modules.badges.modal.unassign-badge.title',
    defaultMessage: 'Remove "{title}" from users',
    description: 'The title of the manual badge removal modal.',
  },
  unassignBadgeModalDescription: {
    id: 'modules.badges.modal.unassign-badge.description',
    defaultMessage: 'Enter the user IDs (usernames) to remove this badge from, one per line or separated by commas.',
    description: 'Instructions shown in the manual badge removal modal.',
  },
  unassignBadgeModalPointsNote: {
    id: 'modules.badges.modal.unassign-badge.points-note',
    defaultMessage: 'Each user will lose up to {points} points.',
    description: 'Note shown when the badge being removed had awarded points.',
  },
  unassignBadgeModalSubmitBtnText: {
    id: 'modules.badges.modal.unassign-badge.button.submit',
    defaultMessage: 'Remove badge',
    description: 'The submit button text in the manual badge removal modal.',
  },
  unassignBadgeModalSelectedCount: {
    id: 'modules.badges.modal.unassign-badge.selected-count',
    defaultMessage: '{count, plural, one {# user} other {# users}} will have this badge removed.',
    description: 'Shows how many distinct user IDs were entered in the removal modal.',
  },

  toastErrorTitle: {
    id: 'modules.badges.toast.error.text',
    defaultMessage: 'Some error occurred.',
    description: 'The text displayed in the error toast message.',
  },
  badgeCreatedTitle: {
    id: 'modules.badges.alert.badge-created.title',
    defaultMessage: 'Badge successfully created',
    description: 'The title for the alert when a badge is successfully created.',
  },
  badgeEditedTitle: {
    id: 'modules.badges.alert.badge-edited.title',
    defaultMessage: 'Badge successfully edited',
    description: 'The title for the alert when a badge is successfully edited.',
  },
  badgeDeletedTitle: {
    id: 'modules.badges.alert.badge-deleted.title',
    defaultMessage: 'Badge successfully deleted',
    description: 'The title for the alert when a badge is successfully deleted.',
  },
  badgeAssignedTitle: {
    id: 'modules.badges.alert.badge-assigned.title',
    defaultMessage: 'Badge assigned: {granted} granted, {already} already had it',
    description: 'The toast shown after manually assigning a badge to users.',
  },
  badgeUnassignedTitle: {
    id: 'modules.badges.alert.badge-unassigned.title',
    defaultMessage: 'Badge removed: {removed} removed, {notAssigned} did not have it',
    description: 'The toast shown after manually removing a badge from users.',
  },
  badgeDraftStatusText: {
    id: 'modules.badges.badge.draft.status.text',
    defaultMessage: 'Draft',
    description: 'The text displayed for the badge status when it is in draft mode.',
  },
  badgeActiveStatusText: {
    id: 'modules.badges.badge.active.status.text',
    defaultMessage: 'Active',
    description: 'The text displayed for the badge status when it is active.',
  },
});

export default messages;

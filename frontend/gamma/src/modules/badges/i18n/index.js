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

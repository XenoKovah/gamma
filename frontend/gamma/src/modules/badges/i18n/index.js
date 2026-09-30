import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.badges.heading.text',
    defaultMessage: 'Accomplishments settings',
    description: 'The text displayed in the heading of the badges settings page.',
  },
  pageDescription: {
    id: 'modules.badges.page.description',
    defaultMessage: 'This page displays accomplishments and allows users to create and edit them.',
    description: 'The description for the badges settings page.',
  },
  addBadgeBtnText: {
    id: 'modules.badges.button.add-badge',
    defaultMessage: 'Add accomplishment',
    description: 'The text displayed on the button to add a badge.',
  },
  totalBadgesCount: {
    id: 'modules.badges.total-badges.counter.text',
    defaultMessage: 'Total accomplishments: {badgesCount}',
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
  badgeExpiryBtnTitle: {
    id: 'modules.badges.badge-item.button.expiry.title',
    defaultMessage: 'Manage expiry',
    description: 'The text on the button that opens the per-user expiry modal of an expiring badge.',
  },
  expiryModalTitle: {
    id: 'modules.badges.modal.expiry.title',
    defaultMessage: 'Manage expiry for "{title}"',
    description: 'The title of the per-user badge expiry modal.',
  },
  expiryModalDescription: {
    id: 'modules.badges.modal.expiry.description',
    defaultMessage: 'Each holder has their own expiry date. Select holders, then set a new date, make them permanent, or expire them now. Points are never changed, and an expired accomplishment comes back if you give it a later date.',
    description: 'Explains the per-user badge expiry modal.',
  },
  expiryModalCloseBtnText: {
    id: 'modules.badges.modal.expiry.close',
    defaultMessage: 'Close',
    description: 'Close button of the expiry modal.',
  },
  expirySetDateBtnText: {
    id: 'modules.badges.modal.expiry.set-date',
    defaultMessage: 'Set expiry date for selected',
    description: 'Primary button that applies the chosen date to the selected holders.',
  },
  expiryMakePermanentBtnText: {
    id: 'modules.badges.modal.expiry.make-permanent',
    defaultMessage: 'Never expire (selected)',
    description: 'Button that clears the expiry of the selected holders.',
  },
  expiryExpireNowBtnText: {
    id: 'modules.badges.modal.expiry.expire-now',
    defaultMessage: 'Expire now (selected)',
    description: 'Button that immediately expires the selected holders grants.',
  },
  expiryDateLabel: {
    id: 'modules.badges.modal.expiry.date-label',
    defaultMessage: 'New expiry date (good through the end of this day, UTC)',
    description: 'Label of the date input in the expiry modal.',
  },
  expiryUserColumn: {
    id: 'modules.badges.modal.expiry.user-column',
    defaultMessage: 'Username',
    description: 'Column heading for the holder username.',
  },
  expiryExpiresColumn: {
    id: 'modules.badges.modal.expiry.expires-column',
    defaultMessage: 'Expires',
    description: 'Column heading for the holder expiry date.',
  },
  expirySelectAll: {
    id: 'modules.badges.modal.expiry.select-all',
    defaultMessage: 'Select all holders',
    description: 'Accessible label of the select-all checkbox.',
  },
  expiryNever: {
    id: 'modules.badges.modal.expiry.never',
    defaultMessage: 'Never',
    description: 'Shown when a grant has no expiry date.',
  },
  expiryExpiredTag: {
    id: 'modules.badges.modal.expiry.expired-tag',
    defaultMessage: 'expired',
    description: 'Tag shown next to the date of an already-expired grant.',
  },
  expiryNoHolders: {
    id: 'modules.badges.modal.expiry.no-holders',
    defaultMessage: 'Nobody holds this accomplishment yet.',
    description: 'Shown when the expiring badge has no holders.',
  },
  expiryUpdatedNotice: {
    id: 'modules.badges.modal.expiry.updated',
    defaultMessage: 'Updated expiry for {count, plural, one {# user} other {# users}}.',
    description: 'Success notice after re-dating grants.',
  },
  expiryExpiredNotice: {
    id: 'modules.badges.modal.expiry.expired',
    defaultMessage: 'Expired {count, plural, one {# grant} other {# grants}} now.',
    description: 'Success notice after immediately expiring grants.',
  },
  expiryError: {
    id: 'modules.badges.modal.expiry.error',
    defaultMessage: 'Something went wrong. Please try again.',
    description: 'Error shown when an expiry request fails.',
  },
  assignBadgeModalExpiryLabel: {
    id: 'modules.badges.modal.assign-badge.expiry-label',
    defaultMessage: 'Expires (optional; leave blank for no expiry)',
    description: 'Label of the optional expiry date when assigning an expiring badge.',
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
    defaultMessage: 'Accomplishment title',
    description: 'The default title for a badge.',
  },
  badgeDefaultDescription: {
    id: 'modules.badges.badge-item.default.description',
    defaultMessage: 'Accomplishment description',
    description: 'The default description for a badge.',
  },
  alertEmptyBadgesListTitle: {
    id: 'modules.badges.alert.empty-badges-list.title',
    defaultMessage: 'No accomplishments available',
    description: 'The title for the alert when there are no badges to display.',
  },
  alertEmptyBadgesListDescription: {
    id: 'modules.badges.alert.empty-badges-list.description',
    defaultMessage: 'There are currently no accomplishments to display.',
    description: 'The description for the alert when there are no badges to display.',
  },
  badgesUncategorizedLabel: {
    id: 'modules.badges.category.uncategorized.label',
    defaultMessage: 'Uncategorized',
    description: 'Heading for the group of accomplishments that have no category set.',
  },
  badgesCategoryCount: {
    id: 'modules.badges.category.count',
    defaultMessage: '{count, plural, one {# accomplishment} other {# accomplishments}}',
    description: 'Count of accomplishments shown next to a category heading in the admin list.',
  },
  addManageEntityModalTitle: {
    id: 'modules.badges.modal.add-badge.title',
    defaultMessage: 'Add new accomplishment',
    description: 'The title for the badge modal.',
  },
  editManageEntityModalTitle: {
    id: 'modules.badges.modal.edit-badge.title',
    defaultMessage: 'Edit accomplishment',
    description: 'The title for the edit badge modal.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.badges.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirm deletion',
    description: 'The title for the confirmation modal when deleting a badge.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.badges.alert.modal.confirm.deletion.description',
    defaultMessage: 'Are you sure you want to delete this accomplishment? This action cannot be undone.',
    description: 'The description for the confirmation modal when deleting a badge.',
  },
  assignBadgeModalTitle: {
    id: 'modules.badges.modal.assign-badge.title',
    defaultMessage: 'Assign "{title}" to users',
    description: 'The title of the manual badge assignment modal.',
  },
  assignBadgeModalDescription: {
    id: 'modules.badges.modal.assign-badge.description',
    defaultMessage: 'Enter the usernames or email addresses to grant this accomplishment to, one per line or separated by commas.',
    description: 'Instructions shown in the manual badge assignment modal.',
  },
  assignBadgeModalPointsNote: {
    id: 'modules.badges.modal.assign-badge.points-note',
    defaultMessage: 'Each user will also receive {points} points.',
    description: 'Note shown when the badge being assigned awards points.',
  },
  assignBadgeModalUserIdsLabel: {
    id: 'modules.badges.modal.assign-badge.user-ids.label',
    defaultMessage: 'Usernames or emails',
    description: 'Label for the usernames/emails textarea in the manual badge assignment modal.',
  },
  assignBadgeModalUserIdsPlaceholder: {
    id: 'modules.badges.modal.assign-badge.user-ids.placeholder',
    defaultMessage: 'e.g. jdoe, asmith@example.com\nor one per line',
    description: 'Placeholder for the usernames/emails textarea in the manual badge assignment modal.',
  },
  assignBadgeModalUnresolvedEmailsError: {
    id: 'modules.badges.modal.assign-badge.unresolved-emails.error',
    defaultMessage: 'No user found for: {emails}. Check the email address, or enter the username instead.',
    description: 'Error shown when one or more entered email addresses could not be matched to a user.',
  },
  assignBadgeModalSubmitBtnText: {
    id: 'modules.badges.modal.assign-badge.button.submit',
    defaultMessage: 'Assign accomplishment',
    description: 'The submit button text in the manual badge assignment modal.',
  },
  assignBadgeModalSelectedCount: {
    id: 'modules.badges.modal.assign-badge.selected-count',
    defaultMessage: '{count, plural, one {# user} other {# users}} will be assigned this accomplishment.',
    description: 'Shows how many distinct user IDs were entered in the assignment modal.',
  },
  unassignBadgeModalTitle: {
    id: 'modules.badges.modal.unassign-badge.title',
    defaultMessage: 'Remove "{title}" from users',
    description: 'The title of the manual badge removal modal.',
  },
  unassignBadgeModalDescription: {
    id: 'modules.badges.modal.unassign-badge.description',
    defaultMessage: 'Enter the usernames or email addresses to remove this accomplishment from, one per line or separated by commas.',
    description: 'Instructions shown in the manual badge removal modal.',
  },
  unassignBadgeModalPointsNote: {
    id: 'modules.badges.modal.unassign-badge.points-note',
    defaultMessage: 'Each user will lose up to {points} points.',
    description: 'Note shown when the badge being removed had awarded points.',
  },
  unassignBadgeModalSubmitBtnText: {
    id: 'modules.badges.modal.unassign-badge.button.submit',
    defaultMessage: 'Remove accomplishment',
    description: 'The submit button text in the manual badge removal modal.',
  },
  unassignBadgeModalSelectedCount: {
    id: 'modules.badges.modal.unassign-badge.selected-count',
    defaultMessage: '{count, plural, one {# user} other {# users}} will have this accomplishment removed.',
    description: 'Shows how many distinct user IDs were entered in the removal modal.',
  },

  toastErrorTitle: {
    id: 'modules.badges.toast.error.text',
    defaultMessage: 'Some error occurred.',
    description: 'The text displayed in the error toast message.',
  },
  badgeCreatedTitle: {
    id: 'modules.badges.alert.badge-created.title',
    defaultMessage: 'Accomplishment successfully created',
    description: 'The title for the alert when a badge is successfully created.',
  },
  badgeEditedTitle: {
    id: 'modules.badges.alert.badge-edited.title',
    defaultMessage: 'Accomplishment successfully edited',
    description: 'The title for the alert when a badge is successfully edited.',
  },
  badgeDeletedTitle: {
    id: 'modules.badges.alert.badge-deleted.title',
    defaultMessage: 'Accomplishment successfully deleted',
    description: 'The title for the alert when a badge is successfully deleted.',
  },
  badgeAssignedTitle: {
    id: 'modules.badges.alert.badge-assigned.title',
    defaultMessage: 'Accomplishment assigned: {granted} granted, {already} already had it',
    description: 'The toast shown after manually assigning a badge to users.',
  },
  badgeUnassignedTitle: {
    id: 'modules.badges.alert.badge-unassigned.title',
    defaultMessage: 'Accomplishment removed: {removed} removed, {notAssigned} did not have it',
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

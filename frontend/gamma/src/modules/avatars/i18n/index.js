import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.avatars.heading.text',
    defaultMessage: 'Avatars settings',
    description: 'The text displayed in the heading of the avatars settings page.',
  },
  pageDescription: {
    id: 'modules.avatars.page.description',
    defaultMessage: 'This page displays badges and allows users to create and edit them.',
    description: 'The description for the avatars settings page.',
  },
  totalAvatarSetsCount: {
    id: 'modules.avatars.total-avatars-sets.counter.text',
    defaultMessage: 'Total avatar sets: {avatarSetsCount}',
    description: 'The text displayed for the total number of avatar sets.',
  },
  addAvatarBtnText: {
    id: 'modules.avatars.button.add-avatar',
    defaultMessage: 'Add avatar',
    description: 'The text displayed on the button to add a avatar.',
  },
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'No avatars available',
    description: 'The title for the alert when there are no avatars to display.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.alert.empty-avatars-list.description',
    defaultMessage: 'There are currently no avatars to display.',
    description: 'The description for the alert when there are no avatars to display.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar-item.button.edit.title',
    defaultMessage: 'Edit',
    description: 'The text displayed on the button to edit a avatar.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar-item.button.delete.title',
    defaultMessage: 'Delete',
    description: 'The text displayed on the button to delete a avatar.',
  },
  toastErrorTitle: {
    id: 'modules.avatars.toast.error.text',
    defaultMessage: 'Some error occurred.',
    description: 'The text displayed in the error toast message.',
  },
  confirmDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.title',
    defaultMessage: 'Confirm deletion',
    description: 'The title for the confirmation modal when deleting a avatar set.',
  },
  confirmDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.description',
    defaultMessage: 'Are you sure you want to delete this avatar set? This action cannot be undone.',
    description: 'The description for the confirmation modal when deleting a avatar set.',
  },
});

export default messages;

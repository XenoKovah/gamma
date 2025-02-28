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
  toastNewAvatarSetCreatedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.created.avatar-set.title',
    defaultMessage: 'New avatar set created successfully',
    description: 'The title for the toast message when a new avatar set is created successfully.',
  },
  toastAvatarSetDeletedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.deleted.avatar-set.title',
    defaultMessage: 'Avatar set successfully deleted',
    description: 'The title for the toast message when a avatar set is deleted successfully.',
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
  avatarStepperBtnStatefulDefaultText: {
    id: 'modules.avatars.stepper.button.stateful.default.text',
    defaultMessage: 'Next',
    description: 'Text for the default state of the stateful button inside the avatar stepper.',
  },
  avatarStepperBtnStatefulPendingText: {
    id: 'modules.avatars.stepper.button.stateful.pending.text',
    defaultMessage: 'Saving',
    description: 'Text for the pending state of the stateful button inside the avatar stepper.',
  },
  avatarStepperBtnStatefulCompleteText: {
    id: 'modules.avatars.stepper.button.stateful.complete.text',
    defaultMessage: 'Saved',
    description: 'Text for the complete state of the stateful button inside the avatar stepper.',
  },
  avatarStepperBtnFinishText: {
    id: 'modules.avatars.stepper.button.finish.text',
    defaultMessage: 'Finish',
    description: 'Text for the finish button inside the avatar stepper.',
  },
  avatarStepperTitle: {
    id: 'modules.avatars.stepper.add-avatar-set.title',
    defaultMessage: 'Add new avatar set',
    description: 'The title for the avatar stepper.',
  },
  avatarStepperValidationTitleRequired: {
    id: 'modules.avatars.stepper.validation.title-required',
    defaultMessage: 'Title is required',
    description: 'The validation message for the title field in the avatar stepper.',
  },
  avatarStepperValidationTitleMaxLength: {
    id: 'modules.avatars.stepper.validation.title-max-length',
    defaultMessage: 'Title must be at most 50 characters long',
    description: 'The validation message for the title field in the avatar stepper.',
  },
  avatarStepperValidationTitleLettersNumbers: {
    id: 'modules.avatars.stepper.validation.title-letters-numbers',
    defaultMessage: 'Title must contain only letters and numbers',
    description: 'The validation message for the title field in the avatar stepper.',
  },
  avatarStepperValidationTitleUnique: {
    id: 'modules.avatars.stepper.validation.title-unique',
    defaultMessage: 'This title already exists',
    description: 'The validation message for the title field in the avatar stepper.',
  },
  avatarStepperCloseBtnTitle: {
    id: 'modules.avatars.stepper.button.close.title',
    defaultMessage: 'Close',
    description: 'The title for the close button in the avatar stepper.',
  },
  avatarStepperAvatarsStepTitle: {
    id: 'modules.avatars.stepper.step.avatars.title',
    defaultMessage: 'Avatars',
    description: 'The title for the avatars step in the avatar stepper.',
  },
  avatarStepperConfigurationStepTitle: {
    id: 'modules.avatars.stepper.step.configuration.title',
    defaultMessage: 'Configuration',
    description: 'The title for the configuration step in the avatar stepper.',
  },
  avatarStepperTitleStepTitle: {
    id: 'modules.avatars.stepper.step.title.title',
    defaultMessage: 'Title',
    description: 'The title for the title step in the avatar stepper.',
  },
  avatarStepperTitleStepDescription: {
    id: 'modules.avatars.stepper.step.title.description',
    defaultMessage: 'Please enter the avatar set title below.',
    description: 'The description for the title step in the avatar stepper.',
  },
  avatarStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.stepper.step.title.input.title.label',
    defaultMessage: 'Enter title',
    description: 'The label for the title input in the title step of the avatar stepper.',
  },
});

export default messages;

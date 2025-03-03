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
  addAvatarSetBtnText: {
    id: 'modules.avatars.button.add-avatar-set',
    defaultMessage: 'Add avatar set',
    description: 'The text displayed on the button to add a new avatar set.',
  },
  alertEmptyAvatarSetListTitle: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.title',
    defaultMessage: 'No avatar sets available',
    description: 'The title for the alert when there are no avatar sets to display.',
  },
  alertEmptyAvatarSetListDescription: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.description',
    defaultMessage: 'There are currently no avatar sets to display.',
    description: 'The description for the alert when there are no avatar sets to display.',
  },
  avatarSetEditBtnTitle: {
    id: 'modules.avatars.avatar-set.button.edit.title',
    defaultMessage: 'Edit',
    description: 'The text displayed on the button to edit a avatar set.',
  },
  avatarSetDeleteBtnTitle: {
    id: 'modules.avatars.avatar-set.button.delete.title',
    defaultMessage: 'Delete',
    description: 'The text displayed on the button to delete a avatar set.',
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
  avatarSetStepperBtnStatefulDefaultText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.default.text',
    defaultMessage: 'Next',
    description: 'Text for the default state of the stateful button inside the avatar set stepper.',
  },
  avatarSetStepperBtnStatefulPendingText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.pending.text',
    defaultMessage: 'Saving',
    description: 'Text for the pending state of the stateful button inside the avatar set stepper.',
  },
  avatarSetStepperBtnStatefulCompleteText: {
    id: 'modules.avatars.avatar-set.stepper.button.stateful.complete.text',
    defaultMessage: 'Saved',
    description: 'Text for the complete state of the stateful button inside the avatar set stepper.',
  },
  avatarSetStepperBtnFinishText: {
    id: 'modules.avatars.avatar-set.stepper.button.finish.text',
    defaultMessage: 'Finish',
    description: 'Text for the finish button inside the avatar set stepper.',
  },
  avatarSetStepperTitle: {
    id: 'modules.avatars.avatar-set.stepper.add-avatar-set.title',
    defaultMessage: 'Add new avatar set',
    description: 'The title for the avatar set stepper.',
  },
  avatarSetStepperValidationTitleRequired: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-required',
    defaultMessage: 'Title is required',
    description: 'The validation message for the title field in the avatar set stepper.',
  },
  avatarSetStepperValidationTitleMaxLength: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-max-length',
    defaultMessage: 'Title must be at most 50 characters long',
    description: 'The validation message for the title field in the avatar set stepper.',
  },
  avatarSetStepperValidationTitleLettersNumbers: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-letters-numbers',
    defaultMessage: 'Title must contain only letters and numbers',
    description: 'The validation message for the title field in the avatar set stepper.',
  },
  avatarSetStepperValidationTitleUnique: {
    id: 'modules.avatars.avatar-set.stepper.validation.title-unique',
    defaultMessage: 'This title already exists',
    description: 'The validation message for the title field in the avatar set stepper.',
  },
  avatarSetStepperCloseBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.close.title',
    defaultMessage: 'Close',
    description: 'The title for the close button in the avatar set stepper.',
  },
  avatarSetStepperAvatarsStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.avatars.title',
    defaultMessage: 'Avatars',
    description: 'The title for the avatars step in the avatar set stepper.',
  },
  avatarSetStepperEvolutionStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.title',
    defaultMessage: 'Evolution',
    description: 'The title for the evolution step in the avatar set stepper.',
  },
  avatarSetStepperTitleStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.title.title',
    defaultMessage: 'Title',
    description: 'The title for the title step in the avatar set stepper.',
  },
  avatarSetStepperTitleStepDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.title.description',
    defaultMessage: 'Please enter the avatar set title below.',
    description: 'The description for the title step in the avatar set stepper.',
  },
  avatarSetStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.avatar-set.stepper.step.title.input.title.label',
    defaultMessage: 'Enter title',
    description: 'The label for the title input in the title step of the avatar set stepper.',
  },
});

export default messages;

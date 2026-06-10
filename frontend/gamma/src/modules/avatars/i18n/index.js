import { defineMessages } from 'react-intl';

const messages = defineMessages({
  pageTitle: {
    id: 'modules.avatars.heading.text',
    defaultMessage: 'Avatars settings',
    description: 'The text displayed in the heading of the avatars settings page.',
  },
  studentAvatarLockedTitle: {
    id: 'modules.avatars.student.avatar.locked.text',
    defaultMessage: 'Character locked',
    description: 'The text displayed on the badge of a locked avatar.',
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
  totalAvatarsCount: {
    id: 'modules.avatars.total-avatars.counter.text',
    defaultMessage: 'Total avatars: {avatarsCount}',
    description: 'The text displayed for the total number of avatars.',
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
  alertEmptyAvatarsListTitle: {
    id: 'modules.avatars.avatars.alert.empty-avatars-list.title',
    defaultMessage: 'At least two avatar stages are required',
    description: 'The title for the alert when there are no avatars to display.',
  },
  alertEmptyAvatarSetListDescription: {
    id: 'modules.avatars.avatar-set.alert.empty-avatar-set-list.description',
    defaultMessage: 'There are currently no avatar sets to display.',
    description: 'The description for the alert when there are no avatar sets to display.',
  },
  alertEmptyAvatarsListDescription: {
    id: 'modules.avatars.avatars.alert.empty-avatar-set-list.description',
    defaultMessage: 'You can add avatar presets in the previous step: Evolution.',
    description: 'The description for the alert when there are no avatars to display, mentioning that presets can be added in the previous step (Evolution).',
  },
  avatarSetEditBtnTitle: {
    id: 'modules.avatars.avatar-set.button.edit.title',
    defaultMessage: 'Edit',
    description: 'The text displayed on the button to edit a avatar set.',
  },
  avatarEditBtnTitle: {
    id: 'modules.avatars.avatar.button.edit.title',
    defaultMessage: 'Edit',
    description: 'The text displayed on the button to edit a avatar.',
  },
  avatarSetDeleteBtnTitle: {
    id: 'modules.avatars.avatar-set.button.delete.title',
    defaultMessage: 'Delete',
    description: 'The text displayed on the button to delete a avatar set.',
  },
  avatarSetDraftBadgeText: {
    id: 'modules.avatars.avatar-set.draft.badge.text',
    defaultMessage: 'Draft',
    description: 'The text displayed on the badge of an avatar set with draft status.',
  },
  avatarDeleteBtnTitle: {
    id: 'modules.avatars.avatar.button.delete.title',
    defaultMessage: 'Delete',
    description: 'The text displayed on the button to delete a avatar.',
  },
  toastErrorTitle: {
    id: 'modules.avatars.toast.error.text',
    defaultMessage: 'Some error occurred.',
    description: 'The text displayed in the error toast message.',
  },
  toastNewAvatarSetSavedSuccessfullyTitle: {
    id: 'modules.avatars.toast.successfully.saved.avatar-set.title',
    defaultMessage: 'Avatar set data saved successfully',
    description: 'The title for the toast message when avatar set data is successfully saved.',
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
  confirmAvatarDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.description',
    defaultMessage: 'Are you sure you want to delete this avatar? This action cannot be undone.',
    description: 'The description for the confirmation modal when deleting a avatar.',
  },
  confirmAvatarStageDeletionModalTitle: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.stage.title',
    defaultMessage: 'Confirm deletion',
    description: 'The title for the confirmation modal when deleting a avatar stage.',
  },
  confirmAvatarStageDeletionModalDescription: {
    id: 'modules.avatars.alert.modal.confirm.deletion.avatar.stage.description',
    defaultMessage: 'Are you sure you want to delete this avatar stage? This action cannot be undone.',
    description: 'The description for the confirmation modal when deleting a avatar stage.',
  },
  editAvatarModalTitle: {
    id: 'modules.avatars.manage.modal.edit-avatar.title',
    defaultMessage: 'Edit avatar',
    description: 'The title for the edit avatar modal.',
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
  avatarSetStepperEditTitle: {
    id: 'modules.avatars.avatar-set.stepper.edit-avatar-set.title',
    defaultMessage: 'Edit avatar set',
    description: 'The title for the edit avatar set stepper.',
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
    defaultMessage: 'Title contains unsupported characters',
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
  avatarSetStepperPreviousBtnTitle: {
    id: 'modules.avatars.avatar-set.stepper.button.previous.title',
    defaultMessage: 'Previous',
    description: 'The title for the previous button in the avatar set stepper.',
  },
  avatarSetStepperFinishStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.finish.title',
    defaultMessage: 'Finish',
    description: 'The title for the finish step in the avatar set stepper.',
  },
  avatarCardRuleSectionTitle: {
    id: 'modules.avatars.avatar-set.card.rule.subsection.title',
    defaultMessage: 'Rule {count}',
    description: 'The title for the rule sub section on the avatar card.',
  },
  avatarCardEventTypeFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.event-type.title',
    defaultMessage: 'Event Type',
    description: 'The title for the event type filter on the avatar card.',
  },
  avatarCardCountFilterTitle: {
    id: 'modules.avatars.avatar-set.card.count.filter.title',
    defaultMessage: 'Count',
    description: 'The title for the count filter on the avatar card.',
  },
  avatarCardIntervalFilterTitle: {
    id: 'modules.avatars.avatar-set.card.interval.filter.title',
    defaultMessage: 'Interval',
    description: 'The title for the interval filter on the avatar card.',
  },
  avatarCardFrequencyFilterTitle: {
    id: 'modules.avatars.avatar-set.card.frequency.filter.title',
    defaultMessage: 'Frequency',
    description: 'The title for the interval filter on the avatar card.',
  },
  avatarCardCourseFilterTitle: {
    id: 'modules.avatars.avatar-set.card.course.filter.title',
    defaultMessage: 'Course',
    description: 'The title for the course filter on the avatar card.',
  },
  avatarCardOrganizationFilterTitle: {
    id: 'modules.avatars.avatar-set.card.organization.filter.title',
    defaultMessage: 'Organization',
    description: 'The title for the organization filter on the avatar card.',
  },
  avatarSetStepperAvatarsStepTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.avatars.title',
    defaultMessage: 'Avatars',
    description: 'The title for the avatars step in the avatar set stepper.',
  },
  avatarSetStepperAvatarsStepSupportText1: {
    id: 'modules.avatars.avatar-set.stepper.step.avatars.support-text-1',
    defaultMessage: 'Edit each avatar stage to set its title, description, and evolution rule. These will be visible to users.',
    description: 'Support text for the avatars step in the avatar set stepper.',
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
  avatarSetStepperTitleStepInputTitleLabel: {
    id: 'modules.avatars.avatar-set.stepper.step.title.input.title.label',
    defaultMessage: 'Enter title',
    description: 'The label for the title input in the title step of the avatar set stepper.',
  },
  avatarSetStepperEvolutionAddStageBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.add-stage.title',
    defaultMessage: 'Add evolution stage',
    description: 'The title for the button to add an evolution stage in the evolution step of the avatar set stepper.',
  },
  avatarSetStepperEvolutionDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.description.text',
    defaultMessage: 'Upload SVG images for the avatar\'s evolution stages (minimum {minCount}, maximum {maxCount}). Max file size: {maxImgSize} MB. At least two stages with uploaded images are required to continue.',
    description: 'The description for the evolution step in the avatar set stepper.',
  },
  avatarSetStepperEvolutionDeleteAvatarBtn: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.button.delete-avatar.text',
    defaultMessage: 'Delete',
    description: 'The text for the button to delete an avatar in the evolution step of the avatar set stepper.',
  },
  avatarSetStepperEvolutionAvatarStageTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.stage.title',
    defaultMessage: 'Stage {index}',
    description: 'The title for the avatar stage in the evolution step of the avatar set stepper.',
  },
  avatarSetStepperEvolutionAvatarDefaultTitle: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.title',
    defaultMessage: 'Title placeholder',
    description: 'The default title for the avatar in the evolution step of the avatar set stepper.',
  },
  avatarSetStepperEvolutionAvatarDefaultDescription: {
    id: 'modules.avatars.avatar-set.stepper.step.evolution.avatar.default.description',
    defaultMessage: 'Some description',
    description: 'The default description for the avatar in the evolution step of the avatar set stepper.',
  },
});

export default messages;

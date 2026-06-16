import { defineMessages } from 'react-intl';

const messages = defineMessages({
  loaderScreenReaderText: {
    id: 'generic.loader.screenReader.text',
    defaultMessage: 'Loading...',
    description: 'Text for screen readers inside the component Loader.',
  },
  alertDangerTitle: {
    id: 'generic.alert.danger.title',
    defaultMessage: 'Error occurred',
    description: 'Title inside the danger Alert component.',
  },
  alertDangerDescription: {
    id: 'generic.alert.danger.description',
    defaultMessage: 'An error occurred while processing your request. Please try again later or contact support if the issue persists.',
    description: 'Description inside the danger Alert component.',
  },
  alertBtnCloseTitle: {
    id: 'generic.alert.button.close.title',
    defaultMessage: 'Dismiss',
    description: 'Title for the close button inside the Alert component.',
  },
  modalDialogBtnCancelText: {
    id: 'generic.modal.dialog.button.cancel.text',
    defaultMessage: 'Cancel',
    description: 'Text for the cancel button inside the modal dialog.',
  },
  modalDialogBtnSubmitText: {
    id: 'generic.modal.dialog.button.submit.text',
    defaultMessage: 'Submit',
    description: 'Text for the submit button inside the modal dialog.',
  },
  alertBtnCancelText: {
    id: 'generic.modal.alert.button.cancel.text',
    defaultMessage: 'Cancel',
    description: 'Text for the cancel button inside the modal alert.',
  },
  alertBtnDeleteText: {
    id: 'generic.modal.alert.button.delete.text',
    defaultMessage: 'Delete',
    description: 'Text for the delete button inside the modal alert.',
  },
  headerBtnSingOutText: {
    id: 'generic.header.button.sing.out.text',
    defaultMessage: 'Sign out',
    description: 'Text for the sign out button inside the header.',
  },
  headerLogoAltText: {
    id: 'generic.header.logo.alt.text',
    defaultMessage: 'Gamification',
    description: 'Alt text for the logo inside the header.',
  },
  'generic.footer.logo.alt.text': {
    id: 'generic.footer.logo.alt.text',
    defaultMessage: 'Gamification',
    description: 'Alt text for the logo inside the footer.',
  },
  btnStatefulDefaultText: {
    id: 'generic.modal.alert.button.stateful.default.text',
    defaultMessage: 'Delete',
    description: 'Text for the default state of the stateful button inside the modal alert.',
  },
  btnStatefulPendingText: {
    id: 'generic.modal.alert.button.stateful.pending.text',
    defaultMessage: 'Deleting',
    description: 'Text for the pending state of the stateful button inside the modal alert.',
  },
  btnStatefulCompleteText: {
    id: 'generic.modal.alert.button.stateful.complete.text',
    defaultMessage: 'Deleted',
    description: 'Text for the complete state of the stateful button inside the modal alert.',
  },
  btnStatefulErrorText: {
    id: 'generic.modal.alert.button.stateful.error.text',
    defaultMessage: 'Error',
    description: 'Text for the error state of the stateful button inside the modal alert.',
  },
  modalDialogBtnStatefulDefaultText: {
    id: 'generic.modal.dialog.button.stateful.default.text',
    defaultMessage: 'Save',
    description: 'Text for the default state of the stateful button inside the modal dialog.',
  },
  modalDialogBtnStatefulPendingText: {
    id: 'generic.modal.dialog.button.stateful.pending.text',
    defaultMessage: 'Saving',
    description: 'Text for the pending state of the stateful button inside the modal dialog.',
  },
  modalDialogBtnStatefulCompleteText: {
    id: 'generic.modal.dialog.button.stateful.complete.text',
    defaultMessage: 'Saved',
    description: 'Text for the complete state of the stateful button inside the modal dialog.',
  },
  modalDialogBtnStatefulErrorText: {
    id: 'generic.modal.dialog.button.stateful.error.text',
    defaultMessage: 'Error',
    description: 'Text for the error state of the stateful button inside the modal dialog.',
  },
  modalEntityValidationTitleRequiredText: {
    id: 'generic.modal.entity.validation.title.required',
    defaultMessage: 'Title is required',
    description: 'Validation message when the title is missing.',
  },
  modalEntityValidationSlugRequiredText: {
    id: 'generic.modal.entity.validation.slug.required',
    defaultMessage: 'Slug is required',
    description: 'Validation message when the slug is missing.',
  },
  modalEntityValidationSlugInvalidText: {
    id: 'generic.modal.entity.validation.slug.invalid',
    defaultMessage: 'Slug can only contain letters, numbers, underscores, and dashes',
    description: 'Validation message when the slug format is incorrect.',
  },
  modalEntityValidationDescriptionRequiredText: {
    id: 'generic.modal.entity.validation.description.required',
    defaultMessage: 'Description is required',
    description: 'Validation message when the description is missing.',
  },
  modalEntityValidationImageRequiredText: {
    id: 'generic.modal.entity.validation.image.required',
    defaultMessage: 'Image is required',
    description: 'Validation message when an image is not uploaded.',
  },
  modalEntityValidationImageSizeText: {
    id: 'generic.modal.entity.validation.image.size',
    defaultMessage: 'File size must be less than {maxSize}MB',
    description: 'Validation message when an uploaded image exceeds the file size limit.',
  },
  modalEntityImageHeadingText: {
    id: 'generic.modal.entity.image.heading',
    defaultMessage: 'Image',
    description: 'The heading for the entity image section in the modal.',
  },
  modalEntityImageBtnUploadText: {
    id: 'generic.modal.entity.image.button.upload',
    defaultMessage: 'Upload image',
    description: 'The text displayed on the button to upload an image for the entity.',
  },
  modalEntityImagePreviewText: {
    id: 'generic.modal.entity.image.preview.screenReader.text',
    defaultMessage: 'Image preview',
    description: 'The screen reader text for the entity image preview.',
  },
  modalEntityInfoHeadingText: {
    id: 'generic.modal.entity.information.heading',
    defaultMessage: 'Base information',
    description: 'The heading for the entity information section in the modal.',
  },
  modalEntityInfoLabelEntityTitle: {
    id: 'generic.modal.entity.information.label.entity.title',
    defaultMessage: 'Title',
    description: 'The label for the entity title in the modal.',
  },
  modalEntityInfoLabelEntitySlugText: {
    id: 'generic.modal.entity.information.label.entity.slug',
    defaultMessage: 'Slug',
    description: 'The label for the entity slug in the modal.',
  },
  modalEntityInfoLabelEntityDescriptionText: {
    id: 'generic.modal.entity.information.label.entity.description',
    defaultMessage: 'Description',
    description: 'The label for the entity description in the modal.',
  },
  modalEntityInfoLabelEntityIsActiveText: {
    id: 'generic.modal.entity.is-active.text',
    defaultMessage: 'Active',
    description: 'The text displayed for the active badge status.',
  },
  modalEntityInfoLabelEntityPointsText: {
    id: 'generic.modal.entity.information.label.entity.points',
    defaultMessage: 'Points (awarded on manual assignment)',
    description: 'The label for the points awarded when a badge is manually assigned to a user.',
  },
  modalEntityInfoLabelEntityManualCriteriaText: {
    id: 'generic.modal.entity.information.label.entity.manual-criteria',
    defaultMessage: 'Manual assignment criteria',
    description: 'The label for the free-text manual assignment criteria shown on hover for manual-only badges.',
  },
  modalEntityInfoLabelEntityCategoryText: {
    id: 'generic.modal.entity.information.label.entity.category',
    defaultMessage: 'Category',
    description: 'The label/placeholder for the free-text badge category used to group and sort badges.',
  },
  modalEntityValidationPointsNumberText: {
    id: 'generic.modal.entity.validation.points.number',
    defaultMessage: 'Points must be a whole number.',
    description: 'Validation message when the points value is not an integer.',
  },
  modalEntityValidationPointsPositiveNumberText: {
    id: 'generic.modal.entity.validation.points.positive',
    defaultMessage: 'Points cannot be negative.',
    description: 'Validation message when the points value is negative.',
  },
  modalEntityRulesTitle: {
    id: 'generic.modal.entity.rules.heading',
    defaultMessage: 'Rules',
    description: 'The heading for the entity rules section in the modal.',
  },
  modalEntityRulesAddNewRuleBtnText: {
    id: 'generic.modal.entity.rules.button.add-new-rule.text',
    defaultMessage: 'Add new rule',
    description: 'The text displayed on the button to add a new rule.',
  },
  modalEntityRulesAlertNoRulesTitle: {
    id: 'generic.modal.entity.rules.alert.no-rules.heading',
    defaultMessage: 'No rules available',
    description: 'The heading for the alert when there are no rules to display.',
  },
  modalEntityRulesAlertNoRulesDescription: {
    id: 'generic.modal.entity.rules.alert.no-rules.description',
    defaultMessage: 'You have not added any rules yet. Click the button below to add your first rule.',
    description: 'The description for the alert when there are no rules to display.',
  },
  modalEntityRulesRuleTitle: {
    id: 'generic.modal.entity.rules.rule.heading',
    defaultMessage: 'Rule {id}',
    description: 'The heading for a rule in the modal.',
  },
  modalEntityRulesRuleEventTypeLabel: {
    id: 'generic.modal.entity.rules.rule.event-type.label',
    defaultMessage: 'Event type',
    description: 'The label for the event type rule in the modal.',
  },
  modalEntityRulesRuleCountLabel: {
    id: 'generic.modal.entity.rules.rule.count.label',
    defaultMessage: 'Count',
    description: 'The label for the count rule in the modal.',
  },
  modalEntityRulesRuleCourseLabel: {
    id: 'generic.modal.entity.rules.rule.course.label',
    defaultMessage: 'Course',
    description: 'The label for the course rule in the modal.',
  },
  modalEntityRulesBtnDeleteText: {
    id: 'generic.modal.entity.rules.button.delete.text',
    defaultMessage: 'Delete rule',
    description: 'The text displayed on the button to delete a rule.',
  },
  modalEntityRulesBtnRemoveFilterText: {
    id: 'generic.modal.entity.rules.button.remove-filter.text',
    defaultMessage: 'Remove',
    description: 'The text displayed on the button to remove a filter.',
  },
  modalEntityRulesIntervalStartLabelText: {
    id: 'generic.modal.entity.rules.interval.start.label.text',
    defaultMessage: 'Start date',
    description: 'The label for the start date interval in the modal.',
  },
  modalEntityRulesIntervalEndLabelText: {
    id: 'generic.modal.entity.rules.interval.end.label.text',
    defaultMessage: 'End date',
    description: 'The label for the end date interval in the modal.',
  },
  modalEntityRulesActionHeadingTitle: {
    id: 'generic.modal.entity.rules.action.heading.text',
    defaultMessage: 'Action',
    description: 'The heading for the action section in the modal.',
  },
  modalEntityRulesFiltersHeadingTitle: {
    id: 'generic.modal.entity.rules.filters.heading.text',
    defaultMessage: 'Filters',
    description: 'The heading for the filters section in the modal.',
  },
  modalEntityRulesFiltersSelectTitle: {
    id: 'generic.modal.entity.rules.filters.select.title',
    defaultMessage: 'Select filter',
    description: 'The title for the select filter in the modal.',
  },
  modalEntityRulesFilterSelectTitle: {
    id: 'generic.modal.entity.rules.filter.select.title',
    defaultMessage: 'Select an {filterName}',
    description: 'The title for the select filter in the modal.',
  },
  modalEntityActionEventNameLabelText: {
    id: 'generic.modal.entity.action.event.name.label',
    defaultMessage: 'Select an {eventType}',
    description: 'The label for the event name action in the modal.',
  },
  modalEntityValidationActionEventNameRequiredText: {
    id: 'generic.modal.entity.action.event.name.validation.text',
    defaultMessage: 'Event type is required',
    description: 'Validation message when the event type is missing.',
  },
  modalEntityValidationActionRequiredText: {
    id: 'generic.modal.entity.action.validation.required.text',
    defaultMessage: 'This field is required',
    description: 'Validation message when the action is missing.',
  },
  modalEntityValidationActionPositiveNumberText: {
    id: 'generic.modal.entity.action.validation.positive-number.text',
    defaultMessage: 'This field must be a positive number',
    description: 'Validation message when the action is not a positive number.',
  },
  modalEntityValidationActionNumberText: {
    id: 'generic.modal.entity.action.validation.number.text',
    defaultMessage: 'This field must be a number',
    description: 'Validation message when the action is not a number.',
  },
  modalEntityValidationStartDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.start-date.required.text',
    defaultMessage: 'Start date is required',
    description: 'Validation message when the start date is missing.',
  },
  modalEntityValidationEndDateRequiredText: {
    id: 'generic.modal.entity.interval.validation.end-date.required.text',
    defaultMessage: 'End date is required',
    description: 'Validation message when the end date is missing.',
  },
  modalEntityValidationFrequencyNumberText: {
    id: 'generic.modal.entity.frequency.validation.int.text',
    defaultMessage: 'Frequency must be a number',
    description: 'Validation message when the frequency is not a number.',
  },
  modalEntityValidationFrequencyPositiveNumberText: {
    id: 'generic.modal.entity.frequency.validation.positive-int.text',
    defaultMessage: 'Frequency must be a positive number',
    description: 'Validation message when the frequency is not a positive number.',
  },
  modalEntityValidationFiltersText: {
    id: 'generic.modal.entity.filters.validation.text',
    defaultMessage: 'is required',
    description: 'Validation message when a filter is missing.',
  },
  modalEntityOrganizationFilterTitle: {
    id: 'generic.modal.entity.organization.filter.title',
    defaultMessage: 'Organization',
    description: 'The title for the organization filter in the modal.',
  },
  modalEntityValidationTitleMaxLengthText: {
    id: 'generic.modal.entity.validation.title.max-length',
    defaultMessage: 'The title must not exceed 100 characters.',
    description: 'Validation message when the title exceeds the maximum allowed length.',
  },
  modalEntityValidationSlugMaxLengthText: {
    id: 'generic.modal.entity.validation.slug.max-length',
    defaultMessage: 'The title must not exceed 30 characters.',
    description: 'Validation message when the slug exceeds the maximum allowed length.',
  },
  modalEntityValidationDescriptionMaxLengthText: {
    id: 'generic.modal.entity.validation.description.max-length',
    defaultMessage: 'The description must not exceed 300 characters.',
    description: 'Validation message when the description exceeds the maximum allowed length.',
  },
  headerBadgesLinkText: {
    id: 'generic.header.nav.badges',
    defaultMessage: 'Accomplishments',
    description: 'The text displayed for the Badges link in the header.',
  },
  headerAvatarsLinkText: {
    id: 'generic.header.nav.avatars',
    defaultMessage: 'Avatars',
    description: 'The text displayed for the Avatars link in the header.',
  },
  headerUserMenuLabel: {
    id: 'generic.header.user-menu.label',
    defaultMessage: 'Account menu for {username}',
    description: 'Accessible label for the per-user navigation dropdown toggle in the header.',
  },
  headerUserMenuPerformance: {
    id: 'generic.header.user-menu.performance',
    defaultMessage: 'Your Accomplishments',
    description: 'User-menu link to the learner performance/accomplishments dashboard.',
  },
  headerUserMenuLeaderboard: {
    id: 'generic.header.user-menu.leaderboard',
    defaultMessage: 'Leaderboard',
    description: 'User-menu link to the leaderboard.',
  },
  headerUserMenuGamificationSettings: {
    id: 'generic.header.user-menu.gamification-settings',
    defaultMessage: 'Gamification Settings',
    description: 'User-menu link to the gamification settings (this admin app).',
  },
  headerUserMenuPublicProfile: {
    id: 'generic.header.user-menu.public-profile',
    defaultMessage: 'Public Profile',
    description: "User-menu link to the learner's public profile page.",
  },
  headerUserMenuAccountSettings: {
    id: 'generic.header.user-menu.account-settings',
    defaultMessage: 'Account Settings',
    description: 'User-menu link to the account settings page.',
  },
  pgnDropzoneDefaultContentLabel: {
    id: 'pgn.Dropzone.DefaultContent.label',
    defaultMessage: 'Drag and drop your file here or click to upload.',
    description: 'The default content label for the Dropzone component.',
  },
  genericManageEntityModalEntityInfoTitle: {
    id: 'generic.manage.entity.modal.entity.info.title',
    defaultMessage: 'Title contains unsupported characters',
    description: 'The validation message for the title field in the manage entity modal.',
  },
});

export default messages;

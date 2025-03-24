import React, { useState, useRef, useCallback } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Formik, Form as FormikForm } from 'formik';

import messages from '../../i18n';
import Modal from '../modal';
import { submitBtnStatuses } from '../status-button';
import EntityImage from './entity-image';
import EntityInfo from './entity-info';
import EntityRules from './entity-rules';
import { getValidationSchema, validateFilters } from './validation';
import { DEFAULT_FORM_VALUES, DEFAULT_ACCEPTED_IMAGE_FORMATS } from './constants';

const ManageEntityModal = ({
  data,
  title,
  onReset,
  submitForm,
  submitStatus,
  setSubmitStatus,
  isManageEntityModalOpen,
  entityAcceptedImageFormats,
}) => {
  const intl = useIntl();
  const [imagePreview, setImagePreview] = useState(null);

  const rulesContainerRef = useRef(null);
  const lastRuleRef = useRef(null);

  const initialFormikValues = data?.entityData || DEFAULT_FORM_VALUES;

  const translations = {
    validation: {
      titleRequired: intl.formatMessage(messages.modalEntityValidationTitleRequiredText),
      titleMaxLength: intl.formatMessage(messages.modalEntityValidationTitleMaxLengthText),
      slug: {
        slugRequired: intl.formatMessage(messages.modalEntityValidationSlugRequiredText),
        slugInvalid: intl.formatMessage(messages.modalEntityValidationSlugInvalidText),
        slugMaxLength: intl.formatMessage(messages.modalEntityValidationSlugMaxLengthText),
      },
      image: {
        imageRequired: intl.formatMessage(messages.modalEntityValidationImageRequiredText),
        imageSize: intl.formatMessage(messages.modalEntityValidationImageSizeText),
      },
      count: {
        countRequired: intl.formatMessage(messages.modalEntityValidationActionCountRequiredText),
        countPositive: intl.formatMessage(messages.modalEntityValidationActionCountPositiveNumberText),
        countInt: intl.formatMessage(messages.modalEntityValidationActionCountNumberText),
      },
      descriptionRequired: intl.formatMessage(messages.modalEntityValidationDescriptionRequiredText),
      descriptionMaxLength: intl.formatMessage(messages.modalEntityValidationDescriptionMaxLengthText),
      eventTypeRequired: intl.formatMessage(messages.modalEntityValidationActionEventNameRequiredText),
      interval: {
        startDateRequired: intl.formatMessage(messages.modalEntityValidationStartDateRequiredText),
        endDateRequired: intl.formatMessage(messages.modalEntityValidationEndDateRequiredText),
      },
      frequency: {
        frequencyInt: intl.formatMessage(messages.modalEntityValidationFrequencyNumberText),
        frequencyPositiveInt: intl.formatMessage(messages.modalEntityValidationFrequencyPositiveNumberText),
      },
      filterKeyRequired: intl.formatMessage(messages.modalEntityValidationFiltersText),
    },
  };

  const handleImageUpload = useCallback((event, setFieldValue) => {
    const file = event.target.files[0];
    if (file) {
      setFieldValue('image', file);
      // Revoke the previous Blob URL to free memory and avoid memory leaks
      if (imagePreview && imagePreview.startsWith('blob:')) {
        URL.revokeObjectURL(imagePreview);
      }

      const objectUrl = URL.createObjectURL(file);
      setImagePreview(objectUrl);
    }
  }, [imagePreview]);

  const handleReset = useCallback(
    (resetForm) => {
      if (resetForm) {
        resetForm();
      }
      setImagePreview(null);
      setSubmitStatus(submitBtnStatuses.DEFAULT);
      if (onReset) {
        onReset();
      }
    },
    [onReset],
  );

  const handleFormSubmit = (values, { resetForm }, updatedData, submitFn, handleResetFn) => {
    if (updatedData.entityData) {
      submitFn(data.entityData.id, values, resetForm, handleResetFn);
      return;
    }
    submitFn(values, resetForm, handleResetFn);
  };

  return (
    <Formik
      initialValues={initialFormikValues}
      enableReinitialize
      validationSchema={() => getValidationSchema(translations.validation, initialFormikValues)}
      validate={(values) => validateFilters(values, translations.validation)}
      onSubmit={(values, formikHelpers) => handleFormSubmit(values, formikHelpers, data, submitForm, handleReset)}
    >
      {({
        handleSubmit, isValid, dirty, resetForm, setFieldValue,
      }) => (
        <Modal
          title={title}
          isOpen={isManageEntityModalOpen}
          handleClose={() => handleReset(resetForm)}
          size="lg"
          hasCloseButton
          isFullscreenOnMobile
          isOverflowVisible={false}
          isBlocking
          submitBtnOptions={{
            submitFn: handleSubmit,
            disabled: !isValid || !dirty,
            isStatefulButton: true,
            submitStatus,
          }}
        >
          <FormikForm className="mt-4">
            <EntityInfo />
            <EntityImage
              imagePreview={imagePreview}
              handleImageUpload={(e) => handleImageUpload(e, setFieldValue)}
              acceptedImageFormats={entityAcceptedImageFormats || DEFAULT_ACCEPTED_IMAGE_FORMATS}
            />
            <EntityRules
              rulesContainerRef={rulesContainerRef}
              lastRuleRef={lastRuleRef}
              data={data}
            />
          </FormikForm>
        </Modal>
      )}
    </Formik>
  );
};

ManageEntityModal.propTypes = {
  isManageEntityModalOpen: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  onReset: PropTypes.func,
  submitForm: PropTypes.func.isRequired,
  submitStatus: PropTypes.oneOf(Object.values(submitBtnStatuses)).isRequired,
  setSubmitStatus: PropTypes.func.isRequired,
  data: PropTypes.shape({
    entityData: PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      title: PropTypes.string,
      slug: PropTypes.string,
      image: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
      description: PropTypes.string,
      eventType: PropTypes.string,
      count: PropTypes.number,
      startDate: PropTypes.string,
      endDate: PropTypes.string,
      frequency: PropTypes.number,
      filters: PropTypes.arrayOf(
        PropTypes.shape({
          key: PropTypes.string.isRequired,
          value: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.bool]).isRequired,
        }),
      ),
    }),
    courses: PropTypes.arrayOf(PropTypes.string),
    organizations: PropTypes.arrayOf(PropTypes.string),
    actions: PropTypes.arrayOf(
      PropTypes.shape({
        eventType: PropTypes.string,
      }),
    ),
  }),
  entityAcceptedImageFormats: PropTypes.arrayOf(PropTypes.string),
};

ManageEntityModal.defaultProps = {
  onReset: null,
  data: {},
  entityAcceptedImageFormats: DEFAULT_ACCEPTED_IMAGE_FORMATS,
};

export default ManageEntityModal;

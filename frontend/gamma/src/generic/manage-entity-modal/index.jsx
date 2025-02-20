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
import { DEFAULT_FORM_VALUES } from './constants';

const ManageEntityModal = ({
  data,
  title,
  onReset,
  submitForm,
  submitStatus,
  setSubmitStatus,
  isManageEntityModalOpen,
}) => {
  const intl = useIntl();
  const [imagePreview, setImagePreview] = useState(null);

  const rulesContainerRef = useRef(null);
  const lastRuleRef = useRef(null);

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
      setImagePreview(URL.createObjectURL(file));
    }
  }, []);

  const handleReset = useCallback(
    (resetForm) => {
      resetForm();
      setImagePreview(null);
      setSubmitStatus(submitBtnStatuses.DEFAULT);
      if (onReset) {
        onReset();
      }
    },
    [onReset],
  );

  return (
    <Formik
      initialValues={DEFAULT_FORM_VALUES}
      validationSchema={() => getValidationSchema(translations.validation)}
      validate={(values) => validateFilters(values, translations.validation)}
      onSubmit={(values, { resetForm }) => {
        submitForm(values, resetForm, handleReset);
      }}
    >
      {({
        handleSubmit, isValid, dirty, resetForm, setFieldValue,
      }) => (
        <Modal
          title={title}
          isOpen={isManageEntityModalOpen}
          handleClose={() => handleReset(resetForm)}
          size="lg"
          variant="dark"
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
    courses: PropTypes.arrayOf(PropTypes.string),
    organizations: PropTypes.arrayOf(PropTypes.string),
    actions: PropTypes.arrayOf(
      PropTypes.shape({
        eventType: PropTypes.string.isRequired,
      }),
    ),
  }),
};

ManageEntityModal.defaultProps = {
  onReset: null,
  data: {},
};

export default ManageEntityModal;

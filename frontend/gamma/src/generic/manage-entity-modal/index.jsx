import React, { useState, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Formik, Form as FormikForm } from 'formik';

import { useTranslate } from '../../i18n/utils';
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
  const [imagePreview, setImagePreview] = useState(null);

  const rulesContainerRef = useRef(null);
  const lastRuleRef = useRef(null);

  const messages = {
    validation: {
      titleRequired: useTranslate('generic.modal.entity.validation.title.required'),
      titleMaxLength: useTranslate('generic.modal.entity.validation.title.max-length'),
      slug: {
        slugRequired: useTranslate('generic.modal.entity.validation.slug.required'),
        slugInvalid: useTranslate('generic.modal.entity.validation.slug.invalid'),
        slugMaxLength: useTranslate('generic.modal.entity.validation.slug.max-length'),
      },
      image: {
        imageRequired: useTranslate('generic.modal.entity.validation.image.required'),
        imageSize: useTranslate('generic.modal.entity.validation.image.size'),
      },
      count: {
        countRequired: useTranslate('generic.modal.entity.action.count.validation.required.text'),
        countPositive: useTranslate('generic.modal.entity.action.count.validation.positive-number.text'),
        countInt: useTranslate('generic.modal.entity.action.count.validation.int.text'),
      },
      descriptionRequired: useTranslate('generic.modal.entity.validation.description.required'),
      descriptionMaxLength: useTranslate('generic.modal.entity.validation.description.max-length'),
      eventTypeRequired: useTranslate('generic.modal.entity.action.event.name.validation.text'),
      interval: {
        startDateRequired: useTranslate('generic.modal.entity.interval.validation.start-date.required.text'),
        endDateRequired: useTranslate('generic.modal.entity.interval.validation.end-date.required.text'),
      },
      frequency: {
        frequencyInt: useTranslate('generic.modal.entity.frequency.validation.int.text'),
        frequencyPositiveInt: useTranslate('generic.modal.entity.frequency.validation.positive-int.text'),
      },
      filterKeyRequired: useTranslate('generic.modal.entity.filters.validation.text'),
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
      validationSchema={() => getValidationSchema(messages.validation)}
      validate={(values) => validateFilters(values, messages.validation)}
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

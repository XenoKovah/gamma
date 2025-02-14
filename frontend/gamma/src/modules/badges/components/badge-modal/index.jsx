import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Formik, Form as FormikForm } from 'formik';

import { useTranslate } from '../../../../i18n/utils';
import { Modal } from '../../../../generic';
import BadgeImage from './badge-image';
import BadgeInformation from './badge-information';
import { getValidationSchema } from './validation';

const BadgeModal = ({ isOpenModalDialog, closeModalDialog }) => {
  const [imagePreview, setImagePreview] = useState(null);

  const handleImageUpload = (event, setFieldValue) => {
    const file = event.target.files[0];
    if (file) {
      setFieldValue('image', file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleReset = (resetForm) => {
    resetForm();
    setImagePreview(null);
    closeModalDialog();
  };

  const messages = {
    addBadgeModalTitle: useTranslate('modules.badges.modal.add-badge.title'),
    validation: {
      titleRequired: useTranslate('modules.badges.modal.validation.title.required'),
      slugRequired: useTranslate('modules.badges.modal.validation.slug.required'),
      slugInvalid: useTranslate('modules.badges.modal.validation.slug.invalid'),
      descriptionRequired: useTranslate('modules.badges.modal.validation.description.required'),
      imageRequired: useTranslate('modules.badges.modal.validation.image.required'),
      imageSize: useTranslate('modules.badges.modal.validation.image.size'),
    },
  };

  return (
    <Formik
      initialValues={{
        title: '', slug: '', description: '', is_active: false, image: null,
      }}
      validationSchema={() => getValidationSchema(messages.validation)}
      onSubmit={({ resetForm }) => handleReset(resetForm)}
    >
      {({
        handleSubmit, isValid, dirty, resetForm, setFieldValue,
      }) => (
        <Modal
          title={messages.addBadgeModalTitle}
          isOpen={isOpenModalDialog}
          handleClose={() => handleReset(resetForm)}
          size="lg"
          variant="dark"
          hasCloseButton
          isFullscreenOnMobile
          isOverflowVisible={false}
          submitBtnOptions={{
            submitFn: handleSubmit,
            disabled: !isValid || !dirty,
          }}
        >
          <FormikForm className="mt-4">
            <BadgeInformation />
            <BadgeImage
              imagePreview={imagePreview}
              handleImageUpload={(e) => handleImageUpload(e, setFieldValue)}
            />
          </FormikForm>
        </Modal>
      )}
    </Formik>
  );
};

BadgeModal.propTypes = {
  isOpenModalDialog: PropTypes.bool.isRequired,
  closeModalDialog: PropTypes.func.isRequired,
};

export default BadgeModal;

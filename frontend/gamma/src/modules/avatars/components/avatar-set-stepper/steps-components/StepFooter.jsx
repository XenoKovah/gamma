import React from 'react';
import PropTypes from 'prop-types';
import { useIntl } from 'react-intl';
import { Button, ActionRow, Stack } from '@openedx/paragon';

import { StatusButton } from '../../../../../generic';
import messages from '../../../i18n';

const StepFooter = ({
  prevBtnText, prevBtnOnClick, nextBtnText, nextBtnOnClick, submitFn, isStatefulBtn,
  disabledNextBtn, submitStatus, statefulButtonLabels, closeBtnOnClick, isFirstStep,
}) => {
  const intl = useIntl();

  return (
    <ActionRow className="avatar-stepper-action-row justify-content-between">
      <Stack direction="horizontal" gap={2}>
        {closeBtnOnClick && (
          <Button variant="outline-primary" onClick={closeBtnOnClick}>
            {intl.formatMessage(messages.avatarSetStepperCloseBtnTitle)}
          </Button>
        )}
      </Stack>
      <Stack direction="horizontal" gap={2}>
        {!isFirstStep && (
          <Button variant="outline-primary" onClick={prevBtnOnClick}>
            {prevBtnText}
          </Button>
        )}
        {isStatefulBtn ? (
          <StatusButton
            variant="primary"
            labels={statefulButtonLabels}
            options={{ submitStatus, submitFn, disabled: disabledNextBtn }}
          />
        ) : (
          <Button onClick={nextBtnOnClick} disabled={disabledNextBtn}>
            {nextBtnText}
          </Button>
        )}
      </Stack>
    </ActionRow>
  );
};

StepFooter.propTypes = {
  prevBtnText: PropTypes.string.isRequired,
  prevBtnOnClick: PropTypes.func,
  nextBtnText: PropTypes.string,
  nextBtnOnClick: PropTypes.func,
  submitFn: PropTypes.func,
  isStatefulBtn: PropTypes.bool,
  disabledNextBtn: PropTypes.bool,
  submitStatus: PropTypes.string,
  statefulButtonLabels: PropTypes.shape({
    default: PropTypes.string,
    pending: PropTypes.string,
    complete: PropTypes.string,
    finish: PropTypes.string,
  }),
  closeBtnOnClick: PropTypes.func,
  isFirstStep: PropTypes.bool,
};

StepFooter.defaultProps = {
  nextBtnText: undefined,
  nextBtnOnClick: () => {},
  submitFn: () => {},
  isStatefulBtn: false,
  disabledNextBtn: false,
  submitStatus: '',
  statefulButtonLabels: {
    default: '',
    pending: '',
    complete: '',
    finish: '',
  },
  closeBtnOnClick: undefined,
  isFirstStep: false,
  prevBtnOnClick: () => {},
};

export default StepFooter;

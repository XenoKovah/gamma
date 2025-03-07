import React from 'react';
import PropTypes from 'prop-types';
import { Button, ActionRow } from '@openedx/paragon';

import { StatusButton } from '../../../../../generic';

const StepFooter = ({
  prevBtnText, prevBtnOnClick, nextBtnText, nextBtnOnClick, submitFn, isStatefulBtn,
  disabled, submitStatus, statefulButtonLabels,
}) => (
  <ActionRow className="avatar-stepper-action-row justify-content-between">
    <Button variant="outline-primary" onClick={prevBtnOnClick}>
      {prevBtnText}
    </Button>
    {isStatefulBtn ? (
      <StatusButton
        variant="primary"
        labels={statefulButtonLabels}
        options={{ submitStatus, submitFn, disabled }}
      />
    ) : (
      <Button onClick={nextBtnOnClick}>
        {nextBtnText}
      </Button>
    )}
  </ActionRow>
);

StepFooter.propTypes = {
  prevBtnText: PropTypes.string.isRequired,
  prevBtnOnClick: PropTypes.func.isRequired,
  nextBtnText: PropTypes.string,
  nextBtnOnClick: PropTypes.func,
  submitFn: PropTypes.func,
  isStatefulBtn: PropTypes.bool,
  disabled: PropTypes.bool,
  submitStatus: PropTypes.string,
  statefulButtonLabels: PropTypes.shape({
    default: PropTypes.string,
    pending: PropTypes.string,
    complete: PropTypes.string,
    finish: PropTypes.string,
  }),
};

StepFooter.defaultProps = {
  nextBtnText: undefined,
  nextBtnOnClick: () => {},
  submitFn: () => {},
  isStatefulBtn: false,
  disabled: false,
  submitStatus: '',
  statefulButtonLabels: {
    default: '',
    pending: '',
    complete: '',
    finish: '',
  },
};

export default StepFooter;

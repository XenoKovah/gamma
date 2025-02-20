import React from 'react';
import PropTypes from 'prop-types';
import { StatefulButton } from '@openedx/paragon';

const StatusButton = ({ variant, options, labels }) => (
  <StatefulButton
    onClick={options?.submitFn}
    disabled={options?.disabled}
    labels={labels}
    variant={variant}
    state={options.submitStatus}
    data-testid="status-button"
  />
);

StatusButton.propTypes = {
  variant: PropTypes.string.isRequired,
  options: PropTypes.shape({
    submitFn: PropTypes.func,
    disabled: PropTypes.bool,
    submitStatus: PropTypes.string,
  }),
  labels: PropTypes.shape({
    default: PropTypes.string.isRequired,
    pending: PropTypes.string,
    complete: PropTypes.string,
    error: PropTypes.string,
  }).isRequired,
};

StatusButton.defaultProps = {
  options: {},
};

export default StatusButton;

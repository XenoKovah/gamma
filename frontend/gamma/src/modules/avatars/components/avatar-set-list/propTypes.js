import PropTypes from 'prop-types';

export const avatarsPropTypes = PropTypes.shape({
  id: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  image: PropTypes.string.isRequired,
  rules: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      action: PropTypes.objectOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])),
      filters: PropTypes.objectOf(PropTypes.string),
    }),
  ),
});

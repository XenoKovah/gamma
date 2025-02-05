import React from 'react';
import { Helmet } from 'react-helmet';
import PropTypes from 'prop-types';

const SEOHelmet = ({ title, description }) => (
  <Helmet>
    <title>{title}</title>
    <meta name="description" content={description} />
  </Helmet>
);

SEOHelmet.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};

export default SEOHelmet;

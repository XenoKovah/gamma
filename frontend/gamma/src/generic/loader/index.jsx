import React from 'react';
import { Spinner } from '@openedx/paragon';

import { useTranslate } from '../../i18n/utils';

const Loader = () => (
  <div className="loader">
    <Spinner
      animation="border"
      screenReaderText={useTranslate('generic.loader.screenReader.text')}
    />
  </div>
);

export default Loader;

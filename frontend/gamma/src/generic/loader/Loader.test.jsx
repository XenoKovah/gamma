import React from 'react';

import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';

import { renderWithProviders } from '../../setupTests';
import messages from '../../i18n/en';
import Loader from './Loader';

afterEach(cleanup);

describe('<Loader>', () => {
  it('renders component', () => {
    const { getByRole } = renderWithProviders(<Loader />);
    const loader = getByRole('status');

    expect(loader).toBeInTheDocument();
  });

  it('has the expected text', () => {
    const content = messages['generic.loader.screenReader.text'].defaultMessage;
    const { getByRole } = renderWithProviders(<Loader />);
    const loader = getByRole('status');

    expect(loader).toHaveTextContent(content);
  });
});

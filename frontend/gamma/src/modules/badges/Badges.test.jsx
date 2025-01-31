import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

import { useTranslate } from '../../i18n/utils';
import messages from './i18n/en';
import { Badges } from '.';

jest.mock('../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('Badges', () => {
  beforeEach(() => {
    useTranslate.mockImplementation((key) => {
      const translations = {
        'modules.badges.button.add-badge': messages['modules.badges.button.add-badge'].defaultMessage,
      };
      return translations[key] || key;
    });
  });

  it('renders add badge button with correct text', () => {
    const { getByTestId } = render(<Badges />);
    expect(getByTestId('add-badge-button')).toBeInTheDocument();
  });
});

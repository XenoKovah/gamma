import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';

import { useTranslate } from '../../../../i18n/utils';
import messages from '../../i18n/en';
import SubHeader from '.';

jest.mock('../../../../i18n/utils', () => ({
  useTranslate: jest.fn(),
}));

describe('SubHeader', () => {
  beforeEach(() => {
    useTranslate.mockImplementation((key, values) => {
      const translations = {
        'modules.badges.heading.text': messages['modules.badges.heading.text'].defaultMessage,
        'modules.badges.total-badges.counter.text':
          messages['modules.badges.total-badges.counter.text'].defaultMessage
            .replace('{badgesCount}', values?.badgesCount || 0),
        'modules.badges.button.add-badge': messages['modules.badges.button.add-badge'].defaultMessage,
      };
      return translations[key] || key;
    });
  });

  it('renders heading, "Add badge" button and total badges count', () => {
    const { getByRole, getByText } = render(<SubHeader />);
    expect(getByRole('heading', {
      level: 1,
    })).toHaveTextContent(messages['modules.badges.heading.text'].defaultMessage);
    expect(getByText(messages['modules.badges.total-badges.counter.text'].defaultMessage
      .replace('{badgesCount}', 0))).toBeInTheDocument();
    expect(getByRole('button', {
      name: messages['modules.badges.button.add-badge'].defaultMessage,
    })).toBeInTheDocument();
  });
});

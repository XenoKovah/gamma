import React from 'react';
import { render } from '@testing-library/react';
import { Helmet } from 'react-helmet';

import SEOHelmet from '.';

describe('SEOHelmet', () => {
  it('renders title and description meta tag correctly', () => {
    const testTitle = 'Test Page Title';
    const testDescription = 'This is a test description for the page.';

    render(<SEOHelmet title={testTitle} description={testDescription} />);

    const helmet = Helmet.peek();
    expect(helmet.title).toBe(testTitle);

    const metaTag = helmet.metaTags.find((meta) => meta.name === 'description');
    expect(metaTag).toBeDefined();
    expect(metaTag.content).toBe(testDescription);
  });
});

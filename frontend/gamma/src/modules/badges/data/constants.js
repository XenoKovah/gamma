import { getCsrfToken } from './utils';

const API_VERSION = '/api/v0';

export const API_ROUTES = {
  BADGES: `${API_VERSION}/badges/`,
  COURSES: `${API_VERSION}/courses/`,
  ORGANIZATIONS: `${API_VERSION}/organizations/`,
  ACTIONS: `${API_VERSION}/available-actions/`,
};

// A getter, so the token is read from the cookie each time the headers are spread into a
// request -- not frozen at page load, when the cookie may be missing or later rotated.
export const REQUEST_HEADERS = {
  get 'X-CSRFToken'() {
    return getCsrfToken();
  },
};

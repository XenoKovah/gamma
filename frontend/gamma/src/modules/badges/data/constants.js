import { getCsrfToken } from './utils';

const API_VERSION = '/api/v0';

export const API_ROUTES = {
  BADGES: `${API_VERSION}/badges/`,
  COURSES: `${API_VERSION}/courses/`,
  ORGANIZATIONS: `${API_VERSION}/organizations/`,
  ACTIONS: `${API_VERSION}/available-actions/?achievement_type=badge`,
};

export const REQUEST_HEADERS = {
  'X-CSRFToken': getCsrfToken(),
};

import { getCsrfToken } from './utils';

const API_VERSION = '/api/v0';

export const API_ROUTES = {
  AVATAR_SET: `${API_VERSION}/avatar_set/`,
  AVATAR: `${API_VERSION}/avatar/`,
  COURSES: `${API_VERSION}/courses/`,
  ORGANIZATIONS: `${API_VERSION}/organizations/`,
  ACTIONS: `${API_VERSION}/actions/`,
};

export const REQUEST_HEADERS = {
  'X-CSRFToken': getCsrfToken(),
};

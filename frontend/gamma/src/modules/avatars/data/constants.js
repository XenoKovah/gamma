import { getCsrfToken } from './utils';

const API_VERSION = '/api/v0';

export const API_ROUTES = {
  AVATAR_SET: `${API_VERSION}/avatar_set/`,
};

export const REQUEST_HEADERS = {
  'X-CSRFToken': getCsrfToken(),
};

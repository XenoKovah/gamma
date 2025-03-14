import { useQuery } from 'react-query';

import {
  fetchActionsData,
  fetchAvatarSetsData,
  fetchCoursesData,
  fetchOrganizationsData,
} from '../api';

/**
 * Custom React Query hooks for fetching data from the API.
 * These hooks automatically manage fetching, caching, and updating data.
*/

export const useAvatarSetsData = () => useQuery('avatarSetsData', fetchAvatarSetsData);

export const useCoursesData = () => useQuery('coursesData', fetchCoursesData);

export const useOrganizationsData = () => useQuery('organizationsData', fetchOrganizationsData);

export const useActionsData = () => useQuery('actionsData', fetchActionsData);

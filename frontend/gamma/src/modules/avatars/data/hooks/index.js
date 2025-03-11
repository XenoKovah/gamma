import { useQuery } from 'react-query';

import {
  fetchActionsData,
  fetchAvatarSetsData,
  fetchCoursesData,
  fetchOrganizationsData,
  fetchStudentAvatarData,
} from '../api';

/**
 * Custom React Query hooks for fetching data from the API.
 * These hooks automatically manage fetching, caching, and updating data.
*/

export const useAvatarSetsData = () => useQuery('avatarSetsData', fetchAvatarSetsData);

// TODO: temp solution to show student experience with avatars.
export const useStudentAvatarData = (avatarSetIdParams, studentUsername) => useQuery(
  ['studentAvatarData'],
  () => fetchStudentAvatarData(avatarSetIdParams, studentUsername),
  { enabled: !!(avatarSetIdParams && studentUsername) },
);

export const useCoursesData = () => useQuery('coursesData', fetchCoursesData);

export const useOrganizationsData = () => useQuery('organizationsData', fetchOrganizationsData);

export const useActionsData = () => useQuery('actionsData', fetchActionsData);

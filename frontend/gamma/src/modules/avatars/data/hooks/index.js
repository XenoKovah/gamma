import { useQuery } from 'react-query';

import { fetchAvatarSetsData } from '../api';

/**
 * Custom React Query hooks for fetching data from the API.
 * These hooks automatically manage fetching, caching, and updating data.
*/

export const useAvatarSetsData = () => useQuery('avatarSetsData', fetchAvatarSetsData);

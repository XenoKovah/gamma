import { useQuery } from 'react-query';

import { fetchBadgesData } from '../api';

/**
 * React Query hook to fetch and cache badge data.
 * @returns {Object} Query result including data, error, and status.
 */
export const useBadgesData = () => useQuery('badgesData', fetchBadgesData);

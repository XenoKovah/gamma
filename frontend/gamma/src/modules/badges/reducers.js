import { DELETION_STATES } from './constants';

export const deletionReducer = (state, action) => {
  if (Object.values(DELETION_STATES).includes(action.type)) {
    return action.type;
  }
  return state;
};

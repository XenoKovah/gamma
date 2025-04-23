import { capitalizeFirstLetter } from '../../../../utils';

export const getFilterConfig = (coursesData, organizationsData, messages) => ({
  course: {
    as: 'select',
    placeholder: capitalizeFirstLetter('course'),
    options: coursesData,
  },
  org: {
    as: 'select',
    placeholder: messages.organizationTitle,
    options: organizationsData,
  },
  frequency: {
    type: 'number',
    placeholder: capitalizeFirstLetter('frequency'),
  },
  interval: {
    type: 'date-range',
  },
});

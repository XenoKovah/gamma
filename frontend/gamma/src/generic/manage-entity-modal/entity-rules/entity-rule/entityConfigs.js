import { capitalizeFirstLetter, sortAlphabetically } from '../../../../utils';

export const getFilterConfig = (coursesData, organizationsData, messages) => ({
  course: {
    as: 'select',
    multiple: true,
    placeholder: capitalizeFirstLetter('course'),
    options: sortAlphabetically(coursesData),
  },
  blocks: {
    multiple: true,
    freeText: true,
    placeholder: capitalizeFirstLetter('blocks'),
  },
  org: {
    as: 'select',
    placeholder: messages.organizationTitle,
    options: sortAlphabetically(organizationsData),
  },
  frequency: {
    type: 'number',
    placeholder: capitalizeFirstLetter('frequency'),
  },
  interval: {
    type: 'date-range',
  },
});

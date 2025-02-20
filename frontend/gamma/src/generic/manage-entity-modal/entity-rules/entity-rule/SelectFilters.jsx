import React, { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { Form } from '@openedx/paragon';
import { useFormikContext } from 'formik';

import { capitalizeFirstLetter } from '../../../../utils';
import { useTranslate } from '../../../../i18n/utils';

const SelectFilters = ({
  rule,
  ruleIndex,
  filterRefs,
  startDateRef,
  AVAILABLE_FILTERS,
}) => {
  const { setFieldValue, validateForm } = useFormikContext();

  const messages = {
    selectFilter: useTranslate('generic.modal.entity.rules.filters.select.title'),
    organizationTitle: useTranslate('generic.modal.entity.organization.filter.title'),
  };

  const addFilter = useCallback(
    (filterName) => {
      if (!filterName || rule.filters[filterName]) {
        return;
      }

      const newFilterValue = filterName === 'interval' ? { start: null, end: null } : '';

      setFieldValue(`rules.${ruleIndex}.filters.${filterName}`, newFilterValue);

      const newFilterRef = React.createRef();
      // eslint-disable-next-line no-param-reassign
      filterRefs.current = { ...filterRefs.current, [filterName]: newFilterRef };

      requestAnimationFrame(() => {
        startDateRef?.current?.input.focus();
        filterRefs.current[filterName]?.current?.focus();
      });

      validateForm();
    },
    [ruleIndex, setFieldValue, validateForm, startDateRef, filterRefs],
  );

  const availableFilters = useMemo(
    () => AVAILABLE_FILTERS.filter((filter) => !(filter in rule.filters)),
    [AVAILABLE_FILTERS, rule.filters],
  );

  return (
    <Form.Group controlId={`addFilter-${ruleIndex}`} size="sm">
      <Form.Control
        as="select"
        className="mr-0"
        onChange={(e) => addFilter(e.target.value)}
      >
        <option value="">{messages.selectFilter}</option>
        {availableFilters.map((filter) => (
          <option key={filter} value={filter}>
            {filter === 'org' ? messages.organizationTitle : capitalizeFirstLetter(filter)}
          </option>
        ))}
      </Form.Control>
    </Form.Group>
  );
};

SelectFilters.propTypes = {
  rule: PropTypes.shape({
    filters: PropTypes.objectOf(PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        start: PropTypes.string,
        end: PropTypes.string,
      }),
    ])).isRequired,
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  startDateRef: PropTypes.shape({
    current: PropTypes.instanceOf(Element),
  }),
  filterRefs: PropTypes.shape({
    current: PropTypes.objectOf(PropTypes.shape({
      current: PropTypes.instanceOf(Element),
    })),
  }).isRequired,
  AVAILABLE_FILTERS: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default SelectFilters;

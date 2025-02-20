import React, { useRef, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { Form, Button, Collapsible } from '@openedx/paragon';
import { useFormikContext } from 'formik';
import classNames from 'classnames';

import { useTranslate } from '../../../../i18n/utils';
import { DATE_TYPES } from '../../constants';
import IntervalDatePicker from './interval-date-picker';
import FilterInputController from './FilterInputController';
import SelectFilters from './SelectFilters';
import ActionField from './ActionField';
import { getActionConfig, getFilterConfig } from './entityConfigs';

const EntityRule = ({
  rule,
  data,
  ruleIndex,
  removeRule,
}) => {
  const {
    values, touched, handleBlur, errors, setFieldValue,
  } = useFormikContext();

  const filterRefs = useRef({});
  const startDateRef = useRef(null);
  const endDateRef = useRef(null);

  const messages = {
    ruleHeading: useTranslate('generic.modal.entity.rules.rule.heading', { id: ruleIndex + 1 }),
    action: useTranslate('generic.modal.entity.rules.action.heading.text'),
    filter: useTranslate('generic.modal.entity.rules.filters.heading.text'),
    organizationTitle: useTranslate('generic.modal.entity.organization.filter.title'),

    eventType: useTranslate('generic.modal.entity.rules.rule.event-type.label'),
    count: useTranslate('generic.modal.entity.rules.rule.count.label'),
    course: useTranslate('generic.modal.entity.rules.rule.course.label'),
    button: {
      deleteRule: useTranslate('generic.modal.entity.rules.button.delete.text'),
      removeFilter: useTranslate('generic.modal.entity.rules.button.remove-filter.text'),
    },
    interval: {
      start: useTranslate('generic.modal.entity.rules.interval.start.label.text'),
      end: useTranslate('generic.modal.entity.rules.interval.end.label.text'),
    },
  };

  const memoizedActionConfig = useMemo(() => getActionConfig(data.actions), []);

  const memoizedFilterConfig = useMemo(() => getFilterConfig(data.courses, data.organizations, messages), [
    data.courses,
    data.organizations,
  ]);

  const AVAILABLE_FILTERS = useMemo(() => Object.keys(memoizedFilterConfig), [memoizedFilterConfig]);

  const handleRemoveFilter = useCallback((filterKey, targetRule) => {
    const newFilters = { ...targetRule.filters };
    delete newFilters[filterKey];
    setFieldValue(`rules.${ruleIndex}.filters`, newFilters);
  }, [ruleIndex, setFieldValue]);

  return (
    <Collapsible
      key={ruleIndex}
      title={messages.ruleHeading}
      styling="card"
      className="entity-rule mb-3"
      defaultOpen
    >
      <h2 className="entity-rule-title h4 mb-3">{messages.action}</h2>

      {Object.entries(memoizedActionConfig).map(([key, config]) => (
        <ActionField
          key={key}
          ruleIndex={ruleIndex}
          name={key}
          type={config.type}
          values={values}
          touched={touched}
          errors={errors}
          setFieldValue={setFieldValue}
          handleBlur={handleBlur}
          label={messages[config.labelKey]}
          options={config.options || []}
        />
      ))}

      <h2 className="entity-rule-title h4 mb-3">{messages.filter}</h2>

      <Form.Group controlId={`rules.${ruleIndex}.filters`} size="sm">
        {Object.keys(rule.filters).map((filterKey) => {
          const config = memoizedFilterConfig[filterKey];

          return (
            <div
              key={filterKey}
              className={classNames('entity-rule-filters mb-3', {
                'entity-rule-filters-interval': filterKey === 'interval',
              })}
            >
              {config?.type !== 'date-range' && (
                <FilterInputController
                  ref={filterRefs.current[filterKey]}
                  filterKey={filterKey}
                  rule={rule}
                  ruleIndex={ruleIndex}
                  {...config}
                />
              )}
              {config?.type === 'date-range' && (
                <>
                  {[DATE_TYPES.START, DATE_TYPES.END].map((dateType) => (
                    <IntervalDatePicker
                      key={dateType}
                      pickerDateRef={dateType === DATE_TYPES.START ? startDateRef : endDateRef}
                      dateType={dateType}
                      rule={rule}
                      ruleIndex={ruleIndex}
                      placeholder={messages.interval[dateType]}
                      isDateTouched={touched.rules?.[ruleIndex]?.filters?.interval?.[dateType]}
                      validationErrorText={errors.rules?.[ruleIndex]?.filters?.interval?.[dateType]}
                    />
                  ))}
                </>
              )}
              <Button
                variant="outline-danger"
                size="sm"
                onClick={() => handleRemoveFilter(filterKey, rule)}
                className="entity-rule-remove-filter-btn ml-2"
              >
                {messages.button.removeFilter}
              </Button>
            </div>
          );
        })}
      </Form.Group>

      {Object.keys(rule.filters).length < AVAILABLE_FILTERS.length && (
        <SelectFilters
          ruleIndex={ruleIndex}
          startDateRef={startDateRef}
          filterRefs={filterRefs}
          AVAILABLE_FILTERS={AVAILABLE_FILTERS}
          rule={rule}
        />
      )}

      <Button variant="danger" size="sm" block onClick={() => removeRule(ruleIndex)}>
        {messages.button.deleteRule}
      </Button>
    </Collapsible>
  );
};

EntityRule.propTypes = {
  rule: PropTypes.shape({
    filters: PropTypes.objectOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.shape({ start: PropTypes.string, end: PropTypes.string }),
      ]),
    ).isRequired,
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  removeRule: PropTypes.func.isRequired,
  data: PropTypes.shape({
    courses: PropTypes.arrayOf(PropTypes.string).isRequired,
    organizations: PropTypes.arrayOf(PropTypes.string).isRequired,
    actions: PropTypes.arrayOf(
      PropTypes.shape({
        eventType: PropTypes.string.isRequired,
      }),
    ).isRequired,
  }),
};

export default EntityRule;

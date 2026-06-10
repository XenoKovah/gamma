import React, { forwardRef, useCallback, useMemo, useState } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import { Form, Button, useMediaQuery, breakpoints } from '@openedx/paragon';

import messages from '../../../../i18n';

const CHARACTER_WIDTH_RATIO = 30;

// A single selection is stored as a plain string (identical to a legacy single-course
// filter); two or more become a list (an OR group). Empty -> '' so "required" still fires.
const normalizeMultiValue = (values) => {
  if (values.length === 0) { return ''; }
  if (values.length === 1) { return values[0]; }
  return values;
};

const FilterInputController = forwardRef(({
  name,
  type,
  as,
  label,
  filterKey,
  rule,
  ruleIndex,
  placeholder,
  multiple,
  freeText,
  options = [],
}, ref) => {
  const intl = useIntl();
  const {
    touched, setFieldValue, setTouched, errors,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });
  const [pendingEntry, setPendingEntry] = useState('');

  const fieldName = `rules.${ruleIndex}.filters.${filterKey}`;
  const fieldValue = rule.filters[filterKey] ?? '';
  const isMulti = multiple && as === 'select';
  const isFreeTextMulti = multiple && freeText;
  const isFieldTouched = touched.rules?.[ruleIndex]?.filters?.[filterKey];
  const validationErrorText = errors.rules?.[ruleIndex]?.filters?.[filterKey];

  const handleBlur = useCallback(() => {
    setTouched({
      ...touched,
      rules: {
        ...touched.rules,
        [ruleIndex]: {
          ...touched.rules?.[ruleIndex],
          filters: {
            ...touched.rules?.[ruleIndex]?.filters,
            [filterKey]: true,
          },
        },
      },
    });
  }, [setTouched, ruleIndex, filterKey]);

  const maxLength = useMemo(() => {
    if (isExtraSmall) {
      return Math.floor(window.innerWidth / CHARACTER_WIDTH_RATIO);
    }
    return Infinity;
  }, [isExtraSmall]);

  const feedback = isFieldTouched && validationErrorText ? (
    <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
      {validationErrorText}
    </Form.Control.Feedback>
  ) : null;

  // Free-text multi-value filter (e.g. the block usage keys a badge is made of).
  // Rendered as a "paste a key -> Add -> removable row" control; the action count is
  // kept in sync with the list length (the "all of these blocks" reading) unless the
  // admin has deliberately set a different count (an "any N of these" rule).
  if (isFreeTextMulti) {
    const selected = Array.isArray(fieldValue) ? fieldValue : (fieldValue ? [fieldValue] : []);

    const syncActionCount = (newLength) => {
      const currentCount = rule.action?.count;
      const tracksListLength = currentCount === '' || currentCount == null
        || Number(currentCount) === selected.length;
      if (tracksListLength) {
        setFieldValue(`rules.${ruleIndex}.action.count`, newLength > 0 ? newLength : '');
      }
    };

    const addPendingEntry = () => {
      const value = pendingEntry.trim();
      if (value && !selected.includes(value)) {
        setFieldValue(fieldName, [...selected, value]);
        syncActionCount(selected.length + 1);
      }
      setPendingEntry('');
    };
    const removeValue = (value) => {
      const remaining = selected.filter((item) => item !== value);
      setFieldValue(fieldName, remaining.length ? remaining : '');
      syncActionCount(remaining.length);
    };

    return (
      <div className="entity-rule-multi-filter">
        <div className="d-flex align-items-start">
          <Form.Control
            ref={ref}
            floatingLabel={label}
            placeholder={placeholder}
            className="entity-rule-filter-form-control mr-2"
            value={pendingEntry}
            onChange={(e) => setPendingEntry(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addPendingEntry();
              }
            }}
            onBlur={handleBlur}
            isInvalid={isFieldTouched && !!validationErrorText}
          />
          <Button
            variant="outline-primary"
            size="sm"
            className="entity-rule-add-filter-btn flex-shrink-0"
            onClick={addPendingEntry}
          >
            {intl.formatMessage(messages.modalEntityRulesBtnAddFilterText)}
          </Button>
        </div>
        <Form.Text>
          Marked complete for every block below (AND) — paste each block&apos;s usage id, e.g.
          block-v1:ORG+Course+Run+type@done+block@… Lower the count for an &quot;any N of these&quot; rule.
        </Form.Text>
        {selected.map((item) => (
          <div key={item} className="d-flex align-items-center justify-content-between mt-1">
            <span className="small text-truncate mr-2" title={item}>{item}</span>
            <Button
              variant="outline-danger"
              size="sm"
              className="entity-rule-remove-filter-btn flex-shrink-0"
              onClick={() => removeValue(item)}
            >
              {intl.formatMessage(messages.modalEntityRulesBtnRemoveFilterText)}
            </Button>
          </div>
        ))}
        {feedback}
      </div>
    );
  }

  // Multi-value filter (e.g. several accepted courses = an OR group). Rendered as a
  // "pick from the dropdown -> add a removable row" control so it needs no modifier keys.
  if (isMulti) {
    const selected = Array.isArray(fieldValue) ? fieldValue : (fieldValue ? [fieldValue] : []);
    const available = options.filter((option) => !selected.includes(option));

    const addValue = (value) => {
      if (value && !selected.includes(value)) {
        setFieldValue(fieldName, normalizeMultiValue([...selected, value]));
      }
    };
    const removeValue = (value) => {
      setFieldValue(fieldName, normalizeMultiValue(selected.filter((item) => item !== value)));
    };

    return (
      <div className="entity-rule-multi-filter">
        <Form.Control
          ref={ref}
          as="select"
          floatingLabel={label}
          className="entity-rule-filter-form-control mr-0"
          value=""
          onChange={(e) => addValue(e.target.value)}
          onBlur={handleBlur}
          isInvalid={isFieldTouched && !!validationErrorText}
        >
          <option value="">
            {intl.formatMessage(messages.modalEntityRulesFilterSelectTitle, { filterName: placeholder })}
          </option>
          {available.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </Form.Control>
        <Form.Text>
          Certificate in any of the courses below (OR) — add each accepted version.
        </Form.Text>
        {selected.map((item) => (
          <div key={item} className="d-flex align-items-center justify-content-between mt-1">
            <span className="small text-truncate mr-2" title={item}>{item}</span>
            <Button
              variant="outline-danger"
              size="sm"
              className="entity-rule-remove-filter-btn flex-shrink-0"
              onClick={() => removeValue(item)}
            >
              {intl.formatMessage(messages.modalEntityRulesBtnRemoveFilterText)}
            </Button>
          </div>
        ))}
        {feedback}
      </div>
    );
  }

  return (
    <>
      <Form.Control
        ref={ref}
        floatingLabel={label}
        name={name}
        placeholder={placeholder}
        className="entity-rule-filter-form-control mr-0"
        as={as}
        type={type}
        value={fieldValue}
        onChange={(e) => setFieldValue(fieldName, e.target.value)}
        onBlur={handleBlur}
        isInvalid={isFieldTouched && !!validationErrorText}
      >
        {as === 'select' ? (
          <>
            <option value="">
              {intl.formatMessage(messages.modalEntityRulesFilterSelectTitle, { filterName: placeholder })}
            </option>
            {options.map((option) => {
              const truncatedOption = isExtraSmall && option.length > maxLength
                ? `${option.slice(0, maxLength)}…`
                : option;

              return (
                <option key={option} value={option}>
                  {truncatedOption}
                </option>
              );
            })}
          </>
        ) : null}
      </Form.Control>
      {feedback}
    </>
  );
});

FilterInputController.propTypes = {
  name: PropTypes.string,
  type: PropTypes.string,
  as: PropTypes.string,
  label: PropTypes.string,
  filterKey: PropTypes.string.isRequired,
  rule: PropTypes.shape({
    filters: PropTypes.objectOf(
      PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.arrayOf(PropTypes.string),
        PropTypes.shape({
          start: PropTypes.string, end: PropTypes.string,
        }),
      ]),
    ).isRequired,
    action: PropTypes.shape({
      count: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    }),
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  placeholder: PropTypes.string,
  multiple: PropTypes.bool,
  freeText: PropTypes.bool,
  options: PropTypes.arrayOf(PropTypes.string),
};

FilterInputController.defaultProps = {
  name: undefined,
  type: undefined,
  label: undefined,
  as: undefined,
  placeholder: undefined,
  multiple: false,
  freeText: false,
  options: [],
};

export default FilterInputController;

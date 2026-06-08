import React, { forwardRef, useCallback, useMemo } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';

import messages from '../../../../i18n';

const CHARACTER_WIDTH_RATIO = 30;

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
  options = [],
}, ref) => {
  const intl = useIntl();
  const {
    touched, setFieldValue, setTouched, errors,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const fieldName = `rules.${ruleIndex}.filters.${filterKey}`;
  const fieldValue = rule.filters[filterKey] ?? '';
  const isMulti = multiple && as === 'select';
  // A multi-value filter (e.g. several accepted courses) is stored as an array, but a single
  // selection stays a plain string so it remains identical to a legacy single-course filter.
  const selectedValues = isMulti
    ? (Array.isArray(fieldValue) ? fieldValue : (fieldValue && [fieldValue]) || [])
    : fieldValue;
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

  const handleChange = useCallback((e) => {
    if (isMulti) {
      const values = Array.from(e.target.selectedOptions, (option) => option.value);
      // 0 -> '' (so "required" validation still fires), 1 -> string (legacy), 2+ -> array (OR group).
      setFieldValue(fieldName, values.length === 0 ? '' : (values.length === 1 ? values[0] : values));
    } else {
      setFieldValue(fieldName, e.target.value);
    }
  }, [isMulti, setFieldValue, fieldName]);

  const maxLength = useMemo(() => {
    if (isExtraSmall) {
      return Math.floor(window.innerWidth / CHARACTER_WIDTH_RATIO);
    }
    return Infinity;
  }, [isExtraSmall]);

  return (
    <>
      <Form.Control
        ref={ref}
        floatingLabel={isMulti ? undefined : label}
        name={name}
        placeholder={placeholder}
        className="entity-rule-filter-form-control mr-0"
        as={as}
        type={type}
        multiple={isMulti}
        value={selectedValues}
        onChange={handleChange}
        onBlur={handleBlur}
        isInvalid={isFieldTouched && !!validationErrorText}
      >
        {as === 'select' ? (
          <>
            {!isMulti && (
              <option value="">
                {intl.formatMessage(messages.modalEntityRulesFilterSelectTitle, { filterName: placeholder })}
              </option>
            )}
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
      {isMulti && (
        <Form.Text className="mb-2">
          Course — certificate in any of the selected courses (Ctrl/Cmd-click to choose several).
        </Form.Text>
      )}
      {isFieldTouched && validationErrorText && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {validationErrorText}
        </Form.Control.Feedback>
      )}
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
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  placeholder: PropTypes.string,
  multiple: PropTypes.bool,
  options: PropTypes.arrayOf(PropTypes.string),
};

FilterInputController.defaultProps = {
  name: undefined,
  type: undefined,
  label: undefined,
  as: undefined,
  placeholder: undefined,
  multiple: false,
  options: [],
};

export default FilterInputController;

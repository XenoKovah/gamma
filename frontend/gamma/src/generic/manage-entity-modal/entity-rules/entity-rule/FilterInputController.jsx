import React, { forwardRef, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import { Form, useMediaQuery, breakpoints } from '@openedx/paragon';

import { useTranslate } from '../../../../i18n/utils';

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
  options = [],
}, ref) => {
  const {
    touched, setFieldValue, setTouched, errors,
  } = useFormikContext();
  const isExtraSmall = useMediaQuery({ maxWidth: breakpoints.extraSmall.maxWidth });

  const messages = {
    filterTitle: useTranslate('generic.modal.entity.rules.filter.select.title', { filterName: placeholder }),
  };

  const fieldName = `rules.${ruleIndex}.filters.${filterKey}`;
  const fieldValue = rule.filters[filterKey] ?? '';
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
            <option value="">{messages.filterTitle}</option>
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
      PropTypes.oneOfType([PropTypes.string, PropTypes.shape({
        start: PropTypes.string, end: PropTypes.string,
      })]),
    ).isRequired,
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  placeholder: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.string),
};

FilterInputController.defaultProps = {
  name: undefined,
  type: undefined,
  label: undefined,
  as: undefined,
  options: [],
};

export default FilterInputController;

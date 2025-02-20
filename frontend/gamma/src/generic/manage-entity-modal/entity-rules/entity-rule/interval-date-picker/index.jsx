import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { useFormikContext } from 'formik';
import DatePicker from 'react-datepicker';
import { Stack, Form } from '@openedx/paragon';
import { enGB } from 'date-fns/locale';

import { DATE_TYPES } from '../../../constants';
import DatePickerFormControl from './DatePickerFormControl';
import { formatDateToISO } from './utils';
import { DATE_FORMAT } from './constants';

const IntervalDatePicker = ({
  pickerDateRef,
  rule,
  ruleIndex,
  dateType,
  placeholder,
  isDateTouched,
  validationErrorText,
  ...props
}) => {
  const { touched, setFieldValue, setTouched } = useFormikContext();

  const isStartDate = dateType === DATE_TYPES.START;
  const isEndDate = dateType === DATE_TYPES.END;
  const intervalFilters = rule.filters.interval || {};

  const hideDatePicker = useCallback((ref) => {
    if (ref?.current) {
      const datePickerRef = ref.current;
      datePickerRef.state.wasHidden = true;
    }
  }, []);

  const handleDateChange = useCallback(
    (date) => {
      const formattedDate = formatDateToISO(date);
      setFieldValue(`rules.${ruleIndex}.filters.interval.${dateType}`, formattedDate);
    },
    [dateType, ruleIndex, setFieldValue],
  );

  const handleDatePickerBlur = () => {
    hideDatePicker(pickerDateRef);
    setTimeout(() => {
      const updatedTouched = { ...touched };
      updatedTouched.rules = updatedTouched.rules || {};
      updatedTouched.rules[ruleIndex] = {
        ...updatedTouched.rules?.[ruleIndex],
        filters: {
          ...updatedTouched.rules[ruleIndex]?.filters,
          interval: {
            ...updatedTouched.rules[ruleIndex]?.filters?.interval,
            [dateType]: true,
          },
        },
      };
      setTouched(updatedTouched);
    }, 50);
  };

  return (
    <Stack className="w-100">
      <DatePicker
        ref={pickerDateRef}
        locale={enGB}
        selected={intervalFilters[dateType] || null}
        dateFormat={DATE_FORMAT}
        placeholderText={placeholder}
        isClearable
        customInput={<DatePickerFormControl className={isStartDate ? 'ml-0' : 'ml-1'} />}
        onSelect={() => hideDatePicker(pickerDateRef)}
        onChange={(date) => handleDateChange(date, dateType)}
        selectsStart={isStartDate}
        selectsEnd={isEndDate}
        startDate={intervalFilters.start ?? null}
        endDate={intervalFilters.end ?? null}
        minDate={isEndDate ? intervalFilters.start ?? null : null}
        onBlur={handleDatePickerBlur}
        {...props}
      />
      {isDateTouched && validationErrorText && (
        <Form.Control.Feedback className="manage-entity-modal-feedback" type="invalid">
          {validationErrorText}
        </Form.Control.Feedback>
      )}
    </Stack>
  );
};

IntervalDatePicker.propTypes = {
  pickerDateRef: PropTypes.shape({
    current: PropTypes.instanceOf(DatePicker),
  }),
  rule: PropTypes.shape({
    filters: PropTypes.shape({
      interval: PropTypes.shape({
        start: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
        end: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
      }),
    }),
  }).isRequired,
  ruleIndex: PropTypes.number.isRequired,
  dateType: PropTypes.oneOf([DATE_TYPES.START, DATE_TYPES.END]).isRequired,
  placeholder: PropTypes.string.isRequired,
  isDateTouched: PropTypes.bool,
  validationErrorText: PropTypes.string,
};

IntervalDatePicker.defaultProps = {
  pickerDateRef: null,
  isDateTouched: false,
  validationErrorText: '',
};

export default IntervalDatePicker;

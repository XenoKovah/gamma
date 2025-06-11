import React, { useCallback } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { Button } from '@openedx/paragon';
import { useFormikContext } from 'formik';
import { v4 as uuidv4 } from 'uuid';

import AlertComponent from '../../alert';
import messages from '../../../i18n';
import EntityRule from './entity-rule';

const EntityRules = ({
  data,
  hasFilters,
  lastRuleRef,
  rulesContainerRef,
}) => {
  const intl = useIntl();
  const {
    values, setFieldValue, setTouched, touched,
  } = useFormikContext();

  const handleAddNewRule = useCallback(() => {
    setFieldValue('rules', [...values.rules, {
      id: uuidv4(),
      action: {},
      filters: {},
    }]);
    requestAnimationFrame(() => {
      if (lastRuleRef.current) {
        lastRuleRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }, [setFieldValue, values.rules]);

  const handleRemoveRule = (index) => {
    setFieldValue('rules', values.rules.filter((_, i) => i !== index));
    setTouched({
      ...touched,
      rules: touched.rules?.filter((_, i) => i !== index),
    });
  };

  return (
    <>
      <h3 className="h4 mb-3">{intl.formatMessage(messages.modalEntityRulesTitle)}</h3>
      <ul className="list-unstyled" ref={rulesContainerRef}>
        {values.rules.length ? (
          values.rules.map((rule, index) => (
            <li key={`rule-${rule.id}`} ref={index === values.rules.length - 1 ? lastRuleRef : null}>
              <EntityRule
                rule={rule}
                ruleIndex={index}
                removeRule={handleRemoveRule}
                data={data}
                hasFilters={hasFilters}
              />
            </li>
          ))
        ) : (
          <li>
            <AlertComponent
              title={intl.formatMessage(messages.modalEntityRulesAlertNoRulesTitle)}
              description={intl.formatMessage(messages.modalEntityRulesAlertNoRulesDescription)}
              variant="info"
            />
          </li>
        )}
      </ul>
      <Button size="sm" block onClick={handleAddNewRule}>
        {intl.formatMessage(messages.modalEntityRulesAddNewRuleBtnText)}
      </Button>
    </>
  );
};

EntityRules.propTypes = {
  data: PropTypes.shape({
    courses: PropTypes.arrayOf(PropTypes.string),
    organizations: PropTypes.arrayOf(PropTypes.string),
    actions: PropTypes.arrayOf(
      PropTypes.shape({
        eventType: PropTypes.string,
      }),
    ),
  }),
  rulesContainerRef: PropTypes.shape({
    current: PropTypes.instanceOf(Element),
  }).isRequired,
  lastRuleRef: PropTypes.shape({
    current: PropTypes.instanceOf(Element),
  }).isRequired,
  hasFilters: PropTypes.bool,
};

EntityRules.defaultProps = {
  hasFilters: false,
};

export default EntityRules;

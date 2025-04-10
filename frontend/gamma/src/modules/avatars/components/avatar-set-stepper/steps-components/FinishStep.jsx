import React, { useMemo } from 'react';
import { useIntl } from 'react-intl';
import PropTypes from 'prop-types';
import { CardGrid, Collapsible, Stepper } from '@openedx/paragon';

import { Card as AvatarCard } from '../../../../../generic';
import { useAvatarsContext } from '../../../context/AvatarsContext';
import moduleMessages from '../../../i18n';
import { sortByDate } from '../../../utils';
import { STEPPER_STEPS } from '../constants';
import StepFooter from './StepFooter';

const FinishStep = ({
  currentStep,
  setCurrentStep,
  avatarSetsData,
  handleFinishAvatarSet,
  handleCloseManageAvatarSetModal,
}) => {
  const intl = useIntl();
  const avatarSetsMap = useMemo(
    () => new Map(avatarSetsData.map(set => [set.id, set])),
    [avatarSetsData],
  );
  const { currentAvatarSetData } = useAvatarsContext();
  const formatDate = (isoString) => isoString.split('T')[0];
  const selectedAvatarSet = avatarSetsMap.get(currentAvatarSetData?.id);

  const filterMessagesMap = {
    count: intl.formatMessage(moduleMessages.avatarCardCountFilterTitle),
    course: intl.formatMessage(moduleMessages.avatarCardCourseFilterTitle),
    interval: intl.formatMessage(moduleMessages.avatarCardIntervalFilterTitle),
    frequency: intl.formatMessage(moduleMessages.avatarCardFrequencyFilterTitle),
    eventType: intl.formatMessage(moduleMessages.avatarCardEventTypeFilterTitle),
    org: intl.formatMessage(moduleMessages.avatarCardOrganizationFilterTitle),
  };

  const isRulesSet = (rules) => Boolean(rules.length);

  const getCardRules = (rules) => {
    if (!isRulesSet(rules)) {
      return null;
    }

    return (
      rules.map((rule, index) => (
        <Collapsible
          key={rule?.id}
          styling="card"
          className="mb-1"
          title={intl.formatMessage(moduleMessages.avatarCardRuleSectionTitle, { count: index + 1 })}
        >
          <ul className="pl-2 small">
            {Object.entries({ ...rule.action, ...rule.filters }).map(([key, value]) => (
              <li key={key}>
                <b>{`${filterMessagesMap[key] || key}: `}</b>
                {key === 'interval' ? `${formatDate(value.start)} - ${formatDate(value.end)}` : value}
              </li>
            ))}
          </ul>
        </Collapsible>
      ))
    );
  };

  const sortedAvatarsMemoized = useMemo(
    () => sortByDate(selectedAvatarSet?.avatars ?? [], 'createdAt'),
    [selectedAvatarSet?.avatars],
  );

  return (
    <>
      <Stepper.Step
        eventKey={STEPPER_STEPS.finish}
        title={intl.formatMessage(moduleMessages.avatarSetStepperFinishStepTitle)}
      >
        <h2 className="my-4">
          {intl.formatMessage(moduleMessages.avatarSetStepperFinishStepTitle)}
        </h2>
        {sortedAvatarsMemoized.length > 0 && (
          <CardGrid
            columnSizes={{ xs: 12, lg: 6, xl: 4 }}
            hasEqualColumnHeights={false}
          >
            {sortedAvatarsMemoized.map(({
              id, title, image, description, rules,
            }) => (
              <AvatarCard
                id={id}
                key={id}
                src={image}
                title={title}
                subtitle={description}
                section={isRulesSet(rules) ? {
                  content: getCardRules(rules),
                } : null}
              />
            ))}
          </CardGrid>
        )}
      </Stepper.Step>
      {currentStep === STEPPER_STEPS.finish && (
        <StepFooter
          prevBtnText={intl.formatMessage(moduleMessages.avatarSetStepperPreviousBtnTitle)}
          prevBtnOnClick={() => setCurrentStep(STEPPER_STEPS.avatars)}
          nextBtnText={intl.formatMessage(moduleMessages.avatarSetStepperBtnFinishText)}
          nextBtnOnClick={() => handleFinishAvatarSet(selectedAvatarSet.id, handleCloseManageAvatarSetModal)}
          closeBtnOnClick={handleCloseManageAvatarSetModal}
        />
      )}
    </>
  );
};

FinishStep.propTypes = {
  currentStep: PropTypes.string.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  handleCloseManageAvatarSetModal: PropTypes.func.isRequired,
  handleFinishAvatarSet: PropTypes.func.isRequired,
  avatarSetsData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      title: PropTypes.string.isRequired,
    }),
  ).isRequired,
};

export default FinishStep;

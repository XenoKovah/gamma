import logging
from typing import List, Union

from django.contrib.contenttypes.models import ContentType

from achievements.exceptions import AchievementRuleProcessingException
from achievements.models import Achievement, AchievementRule
from avatars.models import Avatar
from badges.models import Badge
from core.base import UseCase
from events.enums import RggInternalEventTypes
from events.models import Event, EventConfiguration
from events.processors import EventProcessorFactory
from events.types import (
    AchievementObtainedDependencies,
    CommonEventDependencies,
    PointsDistributionEventDependencies
)
from events.utils import simulate_rgg_internal_event
from rules.models import Rule
from users.models import GammaUser

logger = logging.getLogger(__name__)


def calculate_rule_dependencies_for_user_based_on_event(
    achievement_rule: AchievementRule,
    user: GammaUser,
    event: Event,
) -> Union[AchievementObtainedDependencies, CommonEventDependencies, PointsDistributionEventDependencies]:
    """
    Process and return the event dependencies for the given rule.
    """
    try:
        event_processor = EventProcessorFactory.get_processor(event.event_name)
        return event_processor.process(achievement_rule, user, event)
    except AchievementRuleProcessingException:
        raise
    except ValueError:
        logger.error(
            'Failed to process event dependencies for achievement rule: (%s, %d).',
            achievement_rule,
            achievement_rule.id,
        )


def collect_fulfilled_rules_for_achievement(achievement: Achievement) -> List[AchievementRule]:
    """
    Collect all the achievement rules associated with a given achievement that have met their goal criteria.
    """
    achievement_rules = AchievementRule.objects.filter(
        achievement=achievement,
        status=AchievementRule.Statuses.ACTIVE,
    )

    return [
        achievement_rule for achievement_rule in achievement_rules
        if achievement_rule.is_dependencies_achieved()
    ]


class CreateUserAchievementBasedOnEventUseCase(UseCase):
    """
    Use case for creating an achievement for the user based on the event and instance.

    Handle the process of following:
    - generate an achievement for the user when a specific event occurs.
    - associate the achievement with the appropriate rules based on event.
    - apply relevant rules to determine whether the achievement can be fulfilled.
    """

    def execute(self, instance: Union[Badge, Avatar], user: GammaUser, event: Event) -> None:
        logger.info('Create achievement for user: %s', user)
        achievement = self._create_achievement(instance, user)
        self._create_rules_for_achievement(achievement, instance, user, event)
        if fulfilled_rules := collect_fulfilled_rules_for_achievement(achievement):
            ProcessFulfilledAchievementRulesUseCase().execute(fulfilled_rules)

        if achievement.all_rules_completed:
            AchievementCompletionUseCase().execute(achievement)

    def _create_achievement(self, instance: Union[Badge, Avatar], user: GammaUser) -> Achievement:
        """
        Create a new achievement for the user.
        """
        content_type = ContentType.objects.get_for_model(type(instance))
        return Achievement.objects.create(
            user=user,
            content_type=content_type,
            object_id=instance.id,
            title=instance.title,
            description=instance.description,
        )

    def _create_rules_for_achievement(
        self,
        achievement: Achievement,
        instance: Union[Badge, Avatar],
        user: GammaUser,
        event: Event
    ):
        """
        Prepare achievement rules based on the instances rules.
        """
        # TODO: processing isn't optimized, but are necessary for unambiguous processing of achievement rules.
        achievement_rules = [self._create_achievement_rule(achievement, rule) for rule in instance.rules.all()]
        for achievement_rule in achievement_rules:
            if achievement_rule.rule.event_configuration == event.configuration:
                try:
                    achievement_rule.dependencies = calculate_rule_dependencies_for_user_based_on_event(
                        achievement_rule, user, event
                    )
                except AchievementRuleProcessingException:
                    logger.warning(
                        'Failed to calculate dependencies for rule %s of achievement %s for user %s.',
                        achievement_rule.rule,
                        achievement.id,
                        user,
                    )
                    achievement_rule.status = AchievementRule.Statuses.FAILED
                    achievement_rule.dependencies = {}

        AchievementRule.objects.bulk_update(achievement_rules, ('dependencies', 'status'))

    def _create_achievement_rule(self, achievement: Achievement, rule: Rule) -> AchievementRule:
        """
        Create a single achievement rule and check if it should be marked as completed.
        """
        event_configuration = EventConfiguration.objects.get(id=rule.event_configuration_id)
        return AchievementRule.objects.create(
            achievement=achievement,
            rule=rule,
            status=AchievementRule.Statuses.ACTIVE,
            points=event_configuration.award,
            dependencies={},
        )


class UpdateUserAchievementBasedOnEventUseCase(UseCase):
    """
    Use case for updating users achievements based on incoming event.

    Handle the process of following:
    - retrieve a user's achievement.
    - update its associated rules.
    - check if any rules are fulfilled based on the provided event.
    """

    def execute(self, instance: Union[Badge, Avatar], user: GammaUser, event: Event) -> None:
        achievement = self._get_user_achievement(instance, user)
        logger.info('Update achievement: %s for user: %s', achievement, user)
        self._update_rules_for_achievement(achievement, instance, user, event)
        if fulfilled_rules := collect_fulfilled_rules_for_achievement(achievement):
            ProcessFulfilledAchievementRulesUseCase().execute(fulfilled_rules)

        if achievement.all_rules_completed:
            AchievementCompletionUseCase().execute(achievement)

    def _get_user_achievement(self, instance: Union[Badge, Avatar], user: GammaUser) -> Achievement:
        """
        Update a draft achievement for the given params with related rules.

        Retrieve the achievement based on the provided parameters and updates the associated rules dependencies.
        Check whether the rules are ready for completion and updates their status accordingly.
        """
        content_type = ContentType.objects.get_for_model(type(instance))
        return Achievement.objects.get(
            user=user,
            content_type=content_type,
            object_id=instance.id,
            title=instance.title,
            description=instance.description,
        )

    def _update_rules_for_achievement(
        self,
        achievement: Achievement,
        instance: Union[Badge, Avatar],
        user: GammaUser,
        event: Event
    ) -> None:
        """
        Update dependencies of the rules of an existing achievement based on changes.
        """
        achievement_rules = AchievementRule.objects.filter(
            achievement=achievement,
            rule__in=instance.rules.all(),
            status=AchievementRule.Statuses.ACTIVE,
            rule__event_configuration=event.configuration,
        )

        for achievement_rule in achievement_rules:
            try:
                dependencies = calculate_rule_dependencies_for_user_based_on_event(achievement_rule, user, event)
                achievement_rule.dependencies = dependencies
            except AchievementRuleProcessingException:
                achievement_rule.status = AchievementRule.Statuses.FAILED
                achievement_rule.dependencies = {}

        AchievementRule.objects.bulk_update(achievement_rules, ('dependencies', 'status'))


class ProcessFulfilledAchievementRulesUseCase(UseCase):
    """
    Use case for processing the achievement rules that are fulfilled.
    """

    def execute(self, fulfilled_rules: List[AchievementRule]) -> None:
        self._process_fulfilled_rules(fulfilled_rules)

    def _process_fulfilled_rules(self, fulfilled_rules: List[AchievementRule]) -> None:
        """
        Process the achievement rules that are fulfilled.
        """
        for achievement_rule in fulfilled_rules:
            achievement_rule.status = AchievementRule.Statuses.COMPLETED
            achievement_rule.save(update_fields=('status',))


class AchievementCompletionUseCase(UseCase):
    """
    Use case for processing the completion of achievement for a user.

    Trigger an internal event to record the achievement
    and issue an avatar to the user upon achievement completion.
    """

    def execute(self, achievement: Achievement):
        simulate_rgg_internal_event(achievement.user, RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value)

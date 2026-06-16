import logging
from typing import List, Union

from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now as timezone_now

from achievements.exceptions import AchievementRuleProcessingException
from achievements.models import Achievement, AchievementRule
from avatars.models import Avatar
from badges.models import Badge
from core.base import UseCase
from events.enums import RggInternalEventTypes
from events.models import Event
from events.processors import EventProcessorFactory
from events.types import EventDependencies
from events.utils import simulate_rgg_internal_event
from rules.models import Rule
from users.models import GammaUser

logger = logging.getLogger(__name__)


def calculate_rule_dependencies_for_user_based_on_event(
    achievement_rule: AchievementRule,
    user: GammaUser,
    event: Event,
) -> EventDependencies:
    """
    Process and return the event dependencies for the given rule.
    """
    try:
        rule_event_name = achievement_rule.rule.event_configuration.event_name
        event_processor = EventProcessorFactory.get_processor(rule_event_name)
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
            try:
                achievement_rule.dependencies = calculate_rule_dependencies_for_user_based_on_event(
                    achievement_rule,
                    user,
                    event
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
        return AchievementRule.objects.create(
            achievement=achievement,
            rule=rule,
            status=AchievementRule.Statuses.ACTIVE,
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
        achievement, _ = Achievement.objects.update_or_create(
            user=user,
            content_type=content_type,
            object_id=instance.id,
            defaults={
                'title': instance.title,
                'description': instance.description,
            }
        )
        return achievement

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
        # Only the first completion records the moment, pays out completion
        # points, and emits the internal "achievement obtained" event. Later
        # events matching an already-complete achievement land here again (the
        # rule may stay selected for the user because another badge/avatar
        # shares it), and must not re-fire.
        if achievement.mark_completed():
            # Badges may carry completion points (Badge.points, shown on the
            # dashboard as "Points for completion"). Pay them out on the first
            # rule-driven completion, mirroring the manual-assignment path
            # (Badge.award_to_user), so the advertised points are granted no
            # matter how the badge is earned. Avatars have no points attribute.
            completion_points = getattr(achievement.content_object, 'points', 0) or 0
            # Apply the badge's points (positive or negative). A negative-points badge
            # earned via a rule docks points -- e.g. a future "completed the course
            # suspiciously fast" rule penalises cheating. ``0`` is skipped (avatars have
            # no points; ``or 0`` above also guards the missing-attribute case).
            if completion_points:
                achievement.user.update_user_points(completion_points)
                achievement.user.update_user_progress(completion_points)
            simulate_rgg_internal_event(achievement.user, RggInternalEventTypes.RGG_ACHIEVEMENT_OBTAINED.value)


class PendingBadgeNotificationsUseCase(UseCase):
    """
    Use case for listing a user's completed-but-not-yet-notified badge achievements.

    Backs the learner-facing "you earned a badge" pop-up: anything returned here is
    a notification waiting to be shown. Only badge achievements are considered —
    avatar achievements have no notification UI.
    """

    def execute(self, user_uid: str) -> List[Achievement]:
        badge_content_type = ContentType.objects.get_for_model(Badge)
        return list(
            Achievement.objects.filter(
                user__user_uid=user_uid,
                content_type=badge_content_type,
                completed_at__isnull=False,
                notification_seen_at__isnull=True,
            ).order_by('completed_at')
        )


class MarkBadgeNotificationsSeenUseCase(UseCase):
    """
    Use case for acknowledging shown badge notifications.

    Stamp ``notification_seen_at`` on the given achievements so they are not
    returned by PendingBadgeNotificationsUseCase again. Idempotent: already-seen
    achievements are left untouched (their original timestamp is preserved).
    """

    def execute(self, user_uid: str, achievement_uuids: List[str]) -> int:
        badge_content_type = ContentType.objects.get_for_model(Badge)
        return Achievement.objects.filter(
            user__user_uid=user_uid,
            content_type=badge_content_type,
            uuid__in=achievement_uuids,
            notification_seen_at__isnull=True,
        ).update(notification_seen_at=timezone_now())

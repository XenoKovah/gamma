from typing import Union, Dict, Tuple

from django.db import models
from django.contrib.contenttypes.models import ContentType

from badges.models import Badge
from core.utils import get_gamification_backends
from events.models import Event, EventConfiguration
from users.models import GammaUser

from .data_classes import UserAction


class AchievementManager(models.Manager):
    """
    Custom manager for the Achievement model, containing logic related to achievements.
    """

    def create_draft_achievement(self, user: GammaUser, event: Event, instance: Union[Badge]) -> None:
        """
        Create a draft achievement for the given params with related rules.
        """
        from .models import AchievementRule

        content_type = ContentType.objects.get_for_model(type(instance))

        achievement = self.create(
            # TODO: user should be taken from params.
            user=GammaUser.objects.last(),
            content_type=content_type,
            object_id=instance.id,
            title=instance.title,
            description=instance.description,
        )

        achievements_rules = self._create_draft_achievement_rules(instance, event, achievement)

        if achievements_rules:
            AchievementRule.objects.bulk_create(achievements_rules)

    def _create_draft_achievement_rules(self, instance: Union[Badge], event: Event, achievement):
        """
        Prepare achievement rules based on the instance's rules.
        """
        from .models import AchievementRule

        achievements_rules = []

        for rule in instance.rules.all():
            events, dependencies = self._parse_rule_actions(rule.action)

            achievements_rules.append(
                AchievementRule(
                    achievement=achievement,
                    rule=rule,
                    status=AchievementRule.Statuses.ACTIVE,
                    points=event.configuration.award,
                    actual_count=events,
                    dependencies=dependencies,
                )
            )

        return achievements_rules

    @staticmethod
    def _parse_rule_actions(actions: dict) -> Tuple[Dict[str, UserAction], Dict[str, str]]:
        """
        Parse rule actions into structured ActionDetail objects.
        """
        events = {}
        dependencies = {}
        available_achievements_backend_names = [backend.NAME for backend in get_gamification_backends()]

        for action_type, value in actions.items():
            if action_type in EventConfiguration.available_event_names():
                events[action_type] = UserAction(
                    count=1,
                    goal=value,
                ).to_dict()
            elif action_type in available_achievements_backend_names:
                dependencies[action_type] = value

        return events, dependencies

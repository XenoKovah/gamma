from datetime import datetime
from typing import Union

from django.contrib.contenttypes.models import ContentType
from django.db import models

from badges.models import Badge
from events.models import Event
from users.models import GammaUser

from .services import RuleDependencyService


class AchievementManager(models.Manager):
    """
    Custom manager for the Achievement model, containing logic related to achievements.
    
    There are methods to handle achievements:
    - create_achievement
    - update_achievement
    """

    def create_achievement(self, user: GammaUser, event: Event, instance: Union[Badge]) -> None:
        """
        Create a draft achievement for the given params with related rules.
        
        It links the achievement to the correct ContentType and associates it with the relevant rules.
        Additionally, prepares the achievement's related rules and determines if any of them are ready for completion.
        """
        content_type = ContentType.objects.get_for_model(type(instance))
        achievement = self.create(
            user=user,
            content_type=content_type,
            object_id=instance.id,
            title=instance.title,
            description=instance.description,
        )

        self._create_achievement_rules(instance, event, achievement)

    def _create_achievement_rules(self, instance: Union[Badge], event: Event, achievement):
        """
        Prepare achievement rules based on the instance's rules.
        """
        from .models import AchievementRule
        
        achievements_rules = [
            self._create_single_achievement_rule(rule, event, achievement)
            for rule in instance.rules.all()
        ]

        if achievements_rules:
            AchievementRule.objects.bulk_create(achievements_rules)

        return achievements_rules
    
    
    def _create_single_achievement_rule(self, rule, event: Event, achievement) -> 'AchievementRule':
        """
        Create a single achievement rule and check if it should be marked as completed.
        """
        from .models import AchievementRule

        dependencies_creator = RuleDependencyService(rule, event.created_at)
        dependencies = dependencies_creator.create_or_update(rule.action)

        achievement_rule = AchievementRule(
            achievement=achievement,
            rule=rule,
            status=AchievementRule.Statuses.ACTIVE,
            points=event.configuration.award,
            dependencies=dependencies,
        )

        if achievement_rule.is_ready_to_complete(achievement.user):
            achievement_rule.status = AchievementRule.Statuses.COMPLETED

        return achievement_rule


    def update_achievement(self, user: GammaUser, event: Event, instance: Union[Badge]) -> None:
        """
        Update a draft achievement for the given params with related rules.
        
        It retrieves the achievement based on the provided parameters and updates the associated rules dependencies.
        It also checks whether the rules are ready for completion and updates their status accordingly.
        """
        content_type = ContentType.objects.get_for_model(type(instance))
        achievement = self.get(
            user=user,
            content_type=content_type,
            object_id=instance.id,
            title=instance.title,
            description=instance.description,
        )

        self._update_achievement_rules(instance, achievement, event.created_at)

    def _update_achievement_rules(self, instance: Union[Badge], achievement, event_created_at: datetime) -> None:
        """
        Update dependencies of the rules of an existing achievement based on changes.
        """
        from .models import AchievementRule

        achievement_rules = AchievementRule.objects.filter(
            achievement=achievement,
            rule__in=instance.rules.all(),
            status=AchievementRule.Statuses.ACTIVE,
        )

        ready_to_complete_rules = []
        for achievement_rule in achievement_rules:
            achievement_rule.update_dependencies(achievement_rule.rule.action, event_created_at)

            if achievement_rule.is_ready_to_complete(achievement.user):
                ready_to_complete_rules.append(achievement_rule)

        AchievementRule.bulk_complete(ready_to_complete_rules)

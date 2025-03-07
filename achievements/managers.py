from datetime import datetime
from typing import Union

from django.contrib.contenttypes.models import ContentType
from django.db import models

from badges.models import Badge
from events.models import Event, EventConfiguration
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

        dependencies_creator = RuleDependencyService(rule, event.created_at, event)
        dependencies = dependencies_creator.create_or_update(rule.action)

        event_configuration = EventConfiguration.objects.get(id=rule.event_configuration_id)

        achievement_rule = AchievementRule(
            achievement=achievement,
            rule=rule,
            status=AchievementRule.Statuses.ACTIVE,
            points=event_configuration.award,
            dependencies=dependencies,
        )

        if self._can_complete_rule(achievement_rule, dependencies, achievement):
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

        self._update_achievement_rules(instance, achievement, event.created_at, event)

    def _update_achievement_rules(self, instance: Union[Badge], achievement, event_created_at: datetime, event) -> None:
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
            achievement_rule.update_dependencies(achievement_rule.rule.action, event_created_at, event)

            if achievement_rule.is_ready_to_complete(achievement.user):
                ready_to_complete_rules.append(achievement_rule)

        AchievementRule.bulk_complete(ready_to_complete_rules)

    def _can_complete_rule(
        self, achievement_rule: 'AchievementRule', dependencies: dict, achievement: 'Achievement'
    ) -> bool:
        """
        Checks whether an achievement_rule can be completed.
        """
        from .models import Achievement

        if achievement_rule.is_ready_to_complete(achievement.user) and 'achievements' not in dependencies:
            return True
        else:
            required_achievements = dependencies.get('achievements', [])
            if not required_achievements:
                return False

            for required_achievement in required_achievements:
                required_achievement_id = required_achievement.get('id')
                required_achievement_obj = Achievement.objects.filter(
                    object_id=required_achievement_id, user=achievement.user
                ).first()
                if required_achievement_obj and required_achievement_obj.all_rules_completed:
                    return True
                return False

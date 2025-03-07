"""
Achievement models.
"""
import uuid
from datetime import datetime
from typing import Dict, List

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .services import RuleDependencyService
from .managers import AchievementManager
from events.models import Event


class Achievement(models.Model):
    """
    Represents an achievement that a user can earn, e.g. Badge, Avatar, Skin.
    """

    user = models.ForeignKey('users.GammaUser', on_delete=models.CASCADE)
    # TODO: We should process uuid somewhere
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    objects = AchievementManager()

    def __str__(self):
        return f'Achievement {self.title!r} with type {self.content_type!r} for {self.user}'

    @property
    def all_rules_completed(self):
        """
        Check if all related AchievementRule instances have the status 'completed'.
        """
        return all(rule.status == AchievementRule.Statuses.COMPLETED for rule in self.achievement_rules.all())


class AchievementRule(models.Model):
    """
    Represents a rule associated with an achievement.
    """

    class Statuses(models.TextChoices):
        ACTIVE = 'active'
        COMPLETED = 'completed'
        FAILED = 'failed'

    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.ACTIVE)

    achievement = models.ForeignKey(
        'achievements.Achievement',
        on_delete=models.CASCADE,
        related_name='achievement_rules',
    )
    rule = models.ForeignKey(
        'rules.Rule',
        on_delete=models.CASCADE,
        related_name='rule_achievements',
    )

    created_at = models.DateTimeField(default=now, editable=False)
    dependencies = models.JSONField(
        default=dict,
        help_text=_(
            'Tracks the current progress for external events and achievement dependencies based on rules action'
        )
    )
    points = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('achievement', 'rule')

    def __str__(self):
        return f'Rule {self.rule.id!r} with status {self.get_status_display()})'

    def update_dependencies(self, actions: Dict[str, int], event_created_at: datetime, event: Event) -> None:
        """
        Update the dependencies dictionary by incrementing values for event based on incoming actions.
        """
        dependencies_updater = RuleDependencyService(self.rule, event_created_at, event, self.dependencies)
        self.dependencies = dependencies_updater.create_or_update(actions)
        self.save(update_fields=('dependencies',))

    def is_ready_to_complete(self, user: 'GammaUser') -> bool:
        """
        Determines whether all dependencies meet their goal criteria.
        
        This checks if:
        - All events are completed based on the rule actions
        - All required achievements are achieved by the current user
        """
        rule_actions = self.rule.action
        if not rule_actions:
            return True

        events_progress = self.dependencies.get('events', {})

        for event_name, event_data in events_progress.items():
            if event_data.get('count', 0) < rule_actions.get(event_name, 0):
                return False

        achievement_progress = self.dependencies.get('achievements', [])
        for achievement in achievement_progress:
            content_type_id = achievement.get('content_type_id')
            object_id = achievement.get('id')
            content_type = ContentType.objects.get_for_id(content_type_id)

            if not Achievement.objects.filter(
                user=user,
                content_type=content_type,
                object_id=object_id,
            ).exists():
                return False

        return True

    @classmethod
    def bulk_complete(cls, achievement_rules: List['AchievementRule']) -> None:
        """
        Bulk update status of given achievement rules to 'complete'.
        """
        if not achievement_rules:
            return

        for achievement_rule in achievement_rules:
            achievement_rule.status = cls.Statuses.COMPLETED

        cls.objects.bulk_update(achievement_rules, ['status'])

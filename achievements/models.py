"""
Achievement models.
"""
import logging
import uuid
from typing import List

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class Achievement(models.Model):
    """
    Represent an achievement that a user can earn, e.g. Badge or Avatar.
    """

    user = models.ForeignKey('users.GammaUser', on_delete=models.CASCADE)
    # TODO: We should process uuid somewhere
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Achievement {self.title!r} with type {self.content_type!r} for {self.user}'

    @property
    def all_rules_completed(self):
        """
        Check if all related AchievementRule instances have the status 'completed'.
        """
        return all(rule.status == AchievementRule.Statuses.COMPLETED for rule in self.achievement_rules.all())

    @property
    def achievement_dependencies(self):
        """
        Receive all Achievement dependencies.
        """
        dependencies_list = []
        for rule in self.achievement_rules.all():
            if hasattr(rule, 'dependencies'):
                dependencies_list.append(rule.dependencies)
        return dependencies_list if dependencies_list else None

    def get_course_related_achievement_rules(self, course_id: str) -> List['AchievementRule']:
        """
        Provide achievement rules with a rule filter for a specific course.
        """
        return [
            achievement_rule for achievement_rule in self.achievement_rules.all()
            if achievement_rule.rule.has_filter('course', course_id)
        ]


class AchievementRule(models.Model):
    """
    Represent a rule associated with an achievement.
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

    # TODO: Restrict rule creation with the same action for one achievement.
    # Now it is possible to create multiple rules with the same action from Admin panel.
    # e.g. {'rgg_points_distribution': {'points': 100}}, {'rgg_points_distribution': {'points': 200}}
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

    class Meta:
        unique_together = ('achievement', 'rule')

    def __str__(self):
        return f'Rule {self.rule.id!r} with status {self.get_status_display()}'

    def is_dependencies_achieved(self) -> bool:
        """
        Determine whether dependencies meet their goal criteria.
        """
        return self.dependencies.get('is_achieved', False)

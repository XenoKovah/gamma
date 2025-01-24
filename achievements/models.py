"""
Achievement models.
"""
import uuid

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .managers import AchievementManager


class Achievement(models.Model):
    """
    Represents an achievement that a user can earn, e.g. Badge, Avatar, Skin.
    """

    user = models.ForeignKey('users.GammaUser', on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    objects = AchievementManager()

    def __str__(self):
        return f'Achievement {self.title!r} with type {self.content_type!r} for {self.user}'


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
    actual_count = models.JSONField(
        default=dict,
        help_text=_("Tracks the current progress for each related event, e.g. {'stop_video': 1}."),
    )
    dependencies = models.JSONField(
        default=dict,
        help_text=_("Stores additional requirements needed to complete this rule, such as {'badge': '101'}."),
    )
    points = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('achievement', 'rule')

    def __str__(self):
        return f'Rule {self.rule.id!r} with status {self.get_status_display()})'

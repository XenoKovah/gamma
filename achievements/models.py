"""
Achievement models.
"""
import uuid

from django.conf import settings
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Achievement(models.Model):
    user = models.ForeignKey('users.GammaUser', on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)


class AchievementRule(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    achievement = models.ForeignKey('achievements.Achievement', on_delete=models.CASCADE, related_name="achievement_rules")
    rule = models.ForeignKey('rules.Rule', on_delete=models.CASCADE, related_name="rule_achievements")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('achievement', 'rule')

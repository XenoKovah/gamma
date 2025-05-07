from typing import Any

from django.db import models
from django.db.models import Exists, OuterRef, QuerySet

from achievements.models import AchievementRule
from core.mixins import TimestampModelMixin
from events.models import EventConfiguration
from users.models import GammaUser


class RuleQuerySet(models.QuerySet):
    """
    Extend queryset manager with rule specific methods.
    """

    def not_completed_by_user(self, configuration: EventConfiguration, user: GammaUser) -> QuerySet['Rule']:
        """
        Filter a list of objects associated with the event configuration that the specified user has not yet completed.
        """
        completed_subquery = AchievementRule.objects.filter(
            rule=OuterRef('pk'),
            achievement__user=user,
            status=AchievementRule.Statuses.COMPLETED,
        )

        return self.filter(
            event_configuration=configuration
        ).annotate(
            user_has_completed=Exists(completed_subquery)
        ).filter(
            user_has_completed=False
        )


class Rule(TimestampModelMixin, models.Model):
    event_configuration = models.ForeignKey(
        'events.EventConfiguration',
        on_delete=models.CASCADE,
        related_name='rules',
        null=True,
    )
    action = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)

    objects = RuleQuerySet.as_manager()

    def __str__(self):
        return f'Rule for {self.action!r}'

    @property
    def is_event_type_relevant(self) -> bool:
        """
        Check if the rule applies to the given event based on event type.
        """
        return self.event_configuration.event_name in self.action

    @property
    def event_content_type(self) -> str:
        """
        Return the content type (related to the dependent badges) of the event configuration.
        """
        return self.event_configuration.content_type

    @classmethod
    def ensure_rule_is_created_from_data(cls, rule_data):
        """
        Get existent or create new Rule from data.
        """
        if (rule := cls.objects.filter(**rule_data).first()) is None:
            rule = cls.objects.create(**rule_data)

        return rule

    def has_filter(self, name: str, value: Any) -> bool:
        """
        Check whether the rule has a filter with a specific value.
        """
        return self.filters.get(name) == value if name in self.filters else False

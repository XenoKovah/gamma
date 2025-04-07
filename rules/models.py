from typing import Any

from django.db import models

from core.mixins import TimestampModelMixin


class Rule(TimestampModelMixin, models.Model):
    event_configuration = models.ForeignKey(
        'events.EventConfiguration',
        on_delete=models.CASCADE,
        related_name='rules',
        null=True,
    )
    action = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)

    def __str__(self):
        return f'Rule for {self.action!r}'

    @property
    def is_event_type_relevant(self) -> bool:
        """
        Check if the rule applies to the given event based on event type.
        """
        return self.event_configuration.event_name in self.action

    @property
    def achievement_content_type(self) -> str:
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

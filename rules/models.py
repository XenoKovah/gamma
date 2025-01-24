from django.db import models


class Rule(models.Model):
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

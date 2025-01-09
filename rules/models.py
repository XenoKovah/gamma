from django.db import models


class Rule(models.Model):
    # Maybe we need to add FK to event config and filter than based on event type?
    event_type = models.ForeignKey('events.EventType', on_delete=models.CASCADE)
    action = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.event_type} - {self.action} - {self.filters}"

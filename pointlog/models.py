from django.db import models
from django.contrib.auth.models import User

from core.models import AppClient


class LoggedEvent(models.Model):
    """
    Model to track incoming events.

    This data structure allow us to check for repeated events by unique_id.
    """
    uniq_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=16)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(AppClient, null=True)

    class Meta:
        unique_together = ('uniq_id', 'client')

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
    event_type = models.CharField(max_length=64)
    org = models.CharField(max_length=128, blank=True)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(AppClient, null=True, on_delete=models.DO_NOTHING)
    rewarded_points = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'uniq_id', 'client')


class ApiAccessEvent(models.Model):
    """
    Model to track incoming events.

    This data structure allow us to check for repeated events by unique_id.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    api_name = models.CharField(max_length=16)

    class Meta:
        unique_together = ('user', 'api_name', 'date')

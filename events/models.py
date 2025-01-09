from django.db import models
from django.utils.timezone import now

from events.constants import COLOR_CHOOCES, NOTIFICATION_MESSAGE_HELP_TEXT


class EventType(models.Model):
    name = models.CharField(max_length=255, verbose_name='Allowed events', unique=True)

    def __str__(self):
        return self.name


class EventConfiguration(models.Model):
    event_type = models.OneToOneField('events.EventType', on_delete=models.CASCADE)
    title = models.CharField(max_length=32, blank=True)
    award = models.PositiveSmallIntegerField(verbose_name='Points to award')
    color = models.PositiveSmallIntegerField(choices=COLOR_CHOOCES, default=1)
    notification_message = models.CharField(
        max_length=128,
        default='You have got {} point.',
        help_text=NOTIFICATION_MESSAGE_HELP_TEXT
    )


class Event(models.Model):
    uid = models.CharField(max_length=255, null=False, blank=False)
    signup_source = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=False, blank=False, db_column='user_uid')

    event_type = models.CharField(max_length=255, null=False, blank=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)

    date = models.DateTimeField(default=now, editable=False)
    client = models.CharField(max_length=255, null=True, blank=True)

    org = models.CharField(max_length=255, null=True, blank=True)
    course_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('uid', 'client', 'username')

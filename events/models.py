from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from events.constants import COLOR_CHOOCES, NOTIFICATION_MESSAGE_HELP_TEXT


class EventType(models.Model):
    """
    Defines the list of allowed event types for tracking in gamification.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Defines a unique event type allowed in the system, such as 'stop_video' or 'edx.bookmark.added'")
    )

    def __str__(self):
        return self.name


class EventConfiguration(models.Model):
    """
    Configuration for each allowed event type without duplication.
    """

    event_type = models.OneToOneField('events.EventType', on_delete=models.CASCADE, related_name='configuration')
    title = models.CharField(max_length=32, blank=True)

    # TODO: Should be refactored as part of user's avatar.
    award = models.PositiveSmallIntegerField(verbose_name=_('Points to award'))
    color = models.PositiveSmallIntegerField(choices=COLOR_CHOOCES, default=1)
    notification_message = models.CharField(
        max_length=128,
        default=_('You have got {} point.'),
        help_text=_(NOTIFICATION_MESSAGE_HELP_TEXT)
    )

    def __str__(self):
        return f'Configuration for event {self.event_type.name!r}'

    @property
    def event_name(self):
        return self.event_type.name


class Event(models.Model):
    """
    Stores incoming event as history records.
    """

    uid = models.CharField(max_length=255, null=False, blank=False)
    signup_source = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=False, blank=False, db_column='user_uid')

    configuration = models.ForeignKey(
        'events.EventConfiguration',
        on_delete=models.CASCADE,
        related_name='event',
        null=True,
    )

    created_at = models.DateTimeField(default=now, editable=False)
    client = models.CharField(max_length=255, null=True, blank=True)

    org = models.CharField(max_length=255, null=True, blank=True)
    course_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('uid', 'client', 'username')

    def __str__(self):
        event_name = getattr(self.configuration, 'event_name', 'Unknown event')
        return f'Event {event_name!r} for course {self.course_id!r} by {self.username!r}'

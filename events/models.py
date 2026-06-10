from typing import List, Optional

from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from events.enums import RggInternalEventTypes
from events.utils import uid_generator


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

    award = models.PositiveSmallIntegerField(verbose_name=_('Points to award'))

    def __str__(self):
        return f'Configuration for event {self.event_type.name!r}'

    @property
    def event_name(self):
        return self.event_type.name

    @classmethod
    def _get_event_names(cls, internal_only: Optional[bool] = None) -> List[str]:
        """
        Retrieve a list of event names filtered by their internal status.
        """
        internal_events = RggInternalEventTypes.get_all()
        qs = cls.objects.all()

        if internal_only is True:
            qs = qs.filter(event_type__name__in=internal_events)
        elif internal_only is False:
            qs = qs.exclude(event_type__name__in=internal_events)

        return list(qs.values_list('event_type__name', flat=True))

    @classmethod
    def all_event_names(cls) -> List[str]:
        """
        Return all event names.
        """
        return cls._get_event_names()

    @classmethod
    def rgg_internal_event_names(cls) -> List[str]:
        """
        Return only internal rgg event names.
        """
        return cls._get_event_names(internal_only=True)

    @classmethod
    def common_event_names(cls) -> List[str]:
        """
        Return only common edx event names.
        """
        return cls._get_event_names(internal_only=False)


class Event(models.Model):
    """
    Stores incoming event as history records.
    """

    uid = models.CharField(max_length=255, null=False, blank=False, default=uid_generator)
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
    block_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        unique_together = ('uid', 'client', 'username')

    def __str__(self):
        event_name = getattr(self.configuration, 'event_name', 'Unknown event')
        return f'Event {event_name!r} for course {self.course_id!r} by {self.username!r}'

    @property
    def event_name(self):
        event_name = getattr(self.configuration, 'event_name', None)
        if not event_name:
            raise ValueError('The event configuration is missing.')
        return event_name

    @classmethod
    def ensure_internal_event_is_created(cls, user: 'GammaUser', configuration: EventConfiguration):
        """
        Ensure an internal event is created for the given user and configuration.
        """
        return cls.objects.create(username=user.user_uid, configuration=configuration)

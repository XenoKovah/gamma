from typing import List, Optional

from django.contrib.contenttypes.models import ContentType
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
    
    is_depends_on_achievement = models.BooleanField(
        default=False,
        help_text=_('Indicates whether the event is used to validate achievement dependencies')
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)

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

    @classmethod
    def all_event_names(cls, is_achievement_dependent: Optional[bool] = None) -> List[str]:
        """
        Returns all available event names.
        """
        queryset = cls.objects.all()

        if is_achievement_dependent is not None:
            queryset = queryset.filter(is_depends_on_achievement=is_achievement_dependent)

        return list(queryset.values_list('event_type__name', flat=True))

    @classmethod
    def available_event_based_names(cls) -> List[str]:
        """
        Return event names that are NOT used for achievement generation.

        Example: 'edx_course_enrollment_activated', 'edx_bookmark_added'.
        """
        return cls.all_event_names(False)

    @classmethod
    def available_achievement_based_names(cls) -> List[str]:
        """
        Return event names that ARE used for achievement generation with dependencies on the other achievements.

        Example: 'rgg_badge_achieved', 'rgg_skin_achieved'.
        """
        return cls.all_event_names(True)


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

    @property
    def event_name(self):
        event_name = getattr(self.configuration, 'event_name', None)
        if not event_name:
            raise ValueError('The event configuration is missing.')
        return event_name

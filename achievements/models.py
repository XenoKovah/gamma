"""
Achievement models.
"""

from django.db import models

from core import db
from core.data_models.models import Status, SystemEvent, Badge


COLOR_CHOOCES = (
    (1, 'Applied Blue'),
    (2, 'Green'),
    (3, 'Yellow'),
    (4, 'Orange'),
    (5, 'Bright Blue'),
    (6, 'Purple'),
    (7, 'Light Gray'),
    (8, 'Red'),
)


BADGE_TYPE_CHOICES = (
    ('video', 'video'),
    ('problem', 'problem'),
    ('course', 'course'),
    ('enrollment', 'enrollment'),
    ('referrer', 'referrer'),
    ('reward', 'reward'),
    ('status', 'status')
)

BADGE_STATUS_COLORS = (
    ('blue', 'blue'),
    ('yellow', 'yellow'),
    ('red', 'red'),
)


class Achievement(models.Model):
    """
    Models for custom achievement.

    We can export new Achievements from
    any new Badges service.
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    badge_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True, null=True)
    badge_img = models.ImageField(upload_to="media")

    def __str__(self):
        return self.slug.__str__()

    @property
    def badge_img_name(self):
        if self.badge_img:
            return self.badge_img.name.split('/')[-1]
    
    def save(self, *args, **kwargs):
        super(Achievement, self).save(*args, **kwargs)
        # TODO remove this
        db.update_badge_skeleton(Badge({
            "badge_uid": self.slug,
            "slug": self.slug,
            "badge_title": self.title,
            "url": self.badge_img.url,
            "active": True
        }))


class StatusBadge(models.Model):
    """
    Models for Status badge.
    """
    title = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    badge_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True, null=True)

    status_points = models.PositiveIntegerField(
        unique=True, blank=True, null=True
    )
    status_color = models.CharField(
        max_length=16, choices=BADGE_STATUS_COLORS, blank=True
    )
    badge_img = models.ImageField(upload_to="media")

    def save(self, *args, **kwargs):
        super(StatusBadge, self).save(*args, **kwargs)
        db.update_status(Status({
            "status_uid": self.slug,
            "slug": self.slug,
            "title": self.title,
            "active": True,
            "points": self.status_points,
            "color": self.status_color,
            "url": self.badge_img.url if self.badge_img else None}))

    def __str__(self):
        return self.slug.__str__()


class Event(models.Model):
    """
    Configiration for incomming event.

    Such as points to give for particular event.
    """
    event_type = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=32, blank=True)
    award = models.PositiveSmallIntegerField(verbose_name='Points to award')
    color = models.PositiveSmallIntegerField(choices=COLOR_CHOOCES, default=1)
    notification_message = models.CharField(
        max_length=128,
        default='You have got {} point.',
        help_text="You can use {} to insert awarded points into correct place. e.g. Congrats! You've earned {} points for watching videos"
    )

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        db.update_event(SystemEvent({
            "event_type": self.event_type,
            "title": self.title,
            "award": self.award,
            "color": self.color,
        }))

    def __unicode__(self):
        return f'{self.event_type}: {self.award} points'

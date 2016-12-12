from django.db import models
from django.contrib.auth.models import User

from .utils import key_secret_generator

from core import signals  # NOQA


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


class GameProfile(models.Model):
    """
    Game User profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    open_badges_id = models.CharField(max_length=128, blank=True)
    points = models.IntegerField(default=0)


class AppClient(models.Model):
    """
    Client application models to hold KEY and SECRET.
    """
    name = models.CharField(max_length=32, unique=True)
    key = models.CharField(max_length=32, unique=True, db_index=True, default=key_secret_generator)
    secret = models.CharField(max_length=32, unique=True, default=key_secret_generator)


class Event(models.Model):
    """
    Configiration for incomming event.

    Such as points to give for particular event.
    """
    event_type = models.CharField(max_length=16, unique=True)
    title = models.CharField(max_length=16, blank=True)
    award = models.PositiveSmallIntegerField(verbose_name='Points to award')
    color = models.PositiveSmallIntegerField(choices=COLOR_CHOOCES, default=1)
    notification_message = models.CharField(
        max_length=128,
        default='You have got {} point.',
        help_text="You can use {} to insert awarded points into correct place. e.g. Congrats! You've earned {} points for watching videos"
    )

    def __unicode__(self):
        return "{0}: {1} points".format(self.event_type, self.award)

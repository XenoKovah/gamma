from django.db import models
from django.contrib.auth.models import User

from .utils import key_secret_generator

from core import signals  # NOQA


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

    def __unicode__(self):
        return "{0}: {1} points".format(self.event_type, self.award)

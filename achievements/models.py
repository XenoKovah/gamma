from django.db import models
from django.contrib.auth.models import User


class Achievement(models.Model):
    """
    Models for custom achievement.

    We can export new Achievements from
    any new Badges service.
    """
    name = models.CharField(max_length=64)
    badge_id = models.CharField(max_length=64, blank=True)
    badge_type = models.CharField(max_length=64)


class UserAchievement(models.Model):
    """
    Custom ManyToMany model for User<=>Achievements relation.
    """
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    achievement = models.ForeignKey(Achievement)

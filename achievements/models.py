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
    description = models.TextField(blank=True, null=True)
    badge_type = models.CharField(max_length=64)
    badge_image = models.ImageField()


class UserAchievement(models.Model):
    """
    Custom ManyToMany model for User<=>Achievements relation.
    """
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    achievement = models.ForeignKey(Achievement)

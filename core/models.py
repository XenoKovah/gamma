from django.db import models
from django.contrib.auth.models import User


class GameProfile(models.Model):
    """
    Game User profile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    open_badges_id = models.CharField(max_length=128, blank=True)
    points = models.IntegerField(default=0)

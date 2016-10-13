from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField

from core.models import Event


BADGE_TYPE_CHOICES = (
    ('video', 'video'),
    ('problem', 'problem'),
    ('course', 'course'),
    ('enrollment', 'enrollment'),
    ('referrer', 'referrer'),
    ('reward', 'reward'),
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
    badge_type = models.CharField(max_length=64, choices=BADGE_TYPE_CHOICES)
    event = models.ForeignKey(Event, null=True, verbose_name='Related event')
    badge_img = FileBrowseField(
        "Image",
        max_length=200,
        directory="badges/",
        extensions=[".png"],
        blank=True,
        null=True
    )

    def __str__(self):
        return self.slug


class UserAchievement(models.Model):
    """
    Custom ManyToMany model for User<=>Achievements relation.
    """
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    achievement = models.ForeignKey(Achievement)

    def __str__(self):
        return '{0} <=> {1} : {2}'.format(self.achievement, self.user.username, self.date)

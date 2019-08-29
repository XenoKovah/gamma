from django.db import models
from django.contrib.auth.models import User
from filebrowser.fields import FileBrowseField


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
        return self.slug
    
    @property
    def badge_img_name(self):
        if self.badge_img:
            return self.badge_img.name.split('/')[-1]


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
    badge_img = badge_img = models.ImageField(upload_to="media")

    def __str__(self):
        return self.slug


class UserAchievement(models.Model):
    """
    Custom ManyToMany model for User<=>Achievements relation.
    """
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} <=> {1} : {2}'.format(self.achievement, self.user.username, self.date)


class UserStatus(models.Model):
    """
    Custom ManyToMany model for User<=>Achievements relation.
    """
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(StatusBadge, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} <=> {1} : {2}'.format(self.status, self.user.username, self.date)


class Event(models.Model):
    """
    Configiration for incomming event.

    Such as points to give for particular event.
    """
    event_type = models.CharField(max_length=64, unique=True)
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
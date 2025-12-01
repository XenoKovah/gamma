from django.contrib.contenttypes.fields import ContentType
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from achievements.models import Achievement
from core.mixins import TimestampModelMixin
from users.models import GammaUser


class Avatar(TimestampModelMixin, models.Model):
    """
    Model representing the Gamma User Avatar.
    """

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Avatar Title'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Avatar Description'))
    image = models.FileField(
        upload_to='uploads/avatars/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
    )
    rules = models.ManyToManyField('rules.Rule', blank=True)
    stage = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=1,
        verbose_name=_('Avatar Stage'),
        validators=[MinValueValidator(1)],
    )

    def __str__(self):
        rules = ', '.join(str(rule.action) for rule in self.rules.all()) if self.rules.exists() else 'No rules'
        return f'Avatar {self.title!r} with rules {rules}'

    class Meta:
        verbose_name = _('Avatar')
        verbose_name_plural = _('Avatars')

    def has_achievement(self, user: GammaUser) -> bool:
        """
        Check whether avatar has any linked achievement via its rules.
        """
        return Achievement.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).exists()


class AvatarSet(TimestampModelMixin, models.Model):
    """
    Model representing a set of Avatars and its attributes.

    A type of evolution where each new object is unlocked based on
    the user's progress, achievements,
    or intermediate results related to the course.
    """

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Avatar Set Title'))
    avatars = models.ManyToManyField(Avatar, blank=True, verbose_name=_('Avatars'))
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Avatar Set')
        verbose_name_plural = _('Avatar Sets')


class UserAvatarConfig(models.Model):
    """
    Model representing the Gamma User's Avatar configuration.
    """

    user = models.OneToOneField(GammaUser, on_delete=models.CASCADE)
    avatar_set = models.ForeignKey(AvatarSet, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.user_uid}'s Avatar Config"

    class Meta:
        verbose_name = _('User Avatar Config')
        verbose_name_plural = _('User Avatar Configs')

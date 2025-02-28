from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import ugettext_lazy as _

from users.models import GammaUser


class Avatar(models.Model):
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

    def __str__(self):
        rules = ', '.join(self.rules.values_list('action', flat=True)) or 'No rules'
        return f'Avatar {self.title!r} with rules {rules}'

    class Meta:
        verbose_name = _('Avatar')
        verbose_name_plural = _('Avatars')


class AvatarSet(models.Model):
    """
    Model representing a set of Avatars and its attributes.

    A type of evolution where each new object is unlocked based on
    the user's progress, achievements,
    or intermediate results related to the course.
    """

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Avatar Set Title'))
    avatars = models.ManyToManyField(Avatar, blank=True, verbose_name=_('Avatars'))
    use_in_courses = models.JSONField(default=list)
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

    user = models.ForeignKey(GammaUser, on_delete=models.CASCADE)
    selected_avatar = models.ForeignKey(Avatar, null=True, blank=True, on_delete=models.CASCADE)
    avatar_set = models.ForeignKey(AvatarSet, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Avatar Config"

    class Meta:
        verbose_name = _('User Avatar Config')
        verbose_name_plural = _('User Avatar Configs')

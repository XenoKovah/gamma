from typing import Optional

from django.contrib.contenttypes.fields import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Count, F, Q, QuerySet
from django.utils.translation import ugettext_lazy as _

from achievements.models import Achievement, AchievementRule
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

    stage = models.PositiveIntegerField(blank=True, null=True, default=None)

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

    def get_last_achieved_avatar(self) -> Optional['Avatar']:
        """
        Return the Avatar in this set with the highest `stage` the user has actually unlocked.

        All achievement rule must be complete.
        If none are achieved, returns None.
        """
        if not self.avatar_set_id or not self.user_id:
            return None

        avatars = (
            self.avatar_set.avatars
            .annotate(
                total_rules=Count('rules', distinct=True),
                completed_rules=Count(
                    'rules',
                    filter=Q(
                        rules__rule_achievements__achievement__user=self.user,
                        rules__rule_achievements__status=AchievementRule.Statuses.COMPLETED,
                        rules__rule_achievements__achievement__object_id__in=self.avatar_set.avatars.values_list(
                            'id', flat=True
                        ),
                    ),
                    distinct=True
                ),
            )
            .filter(total_rules=F('completed_rules'))
            .order_by('-stage')
        )

        return avatars.first()

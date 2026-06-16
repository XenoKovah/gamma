from django.contrib.contenttypes.fields import ContentType
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now

from achievements.models import Achievement
from users.models import GammaUser
from core.mixins import TimestampModelMixin


class Badge(TimestampModelMixin, models.Model):
    """
    Reward given to users for achieving specific conditions defined by rules.
    """

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text='Free-text grouping label for the badge. Used to sort badges on the all-badges page.',
    )
    image = models.ImageField(upload_to='uploads/badges/')
    is_active = models.BooleanField(default=True)

    points = models.IntegerField(
        default=0,
        help_text=(
            'Points granted to a user when this badge is assigned to them — manually by an admin, '
            'or automatically when its completion rules are met. May be negative to dock points as a penalty.'
        ),
    )
    manual_criteria = models.TextField(
        blank=True,
        default='',
        help_text=(
            'For manually-assigned (rule-less) badges: free text describing how this badge is '
            'granted. Shown to learners on hover, separately from the description.'
        ),
    )

    slug = models.SlugField(max_length=255, null=True, blank=True)
    rules = models.ManyToManyField('rules.Rule')

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        rules = ', '.join(str(rule.action) for rule in self.rules.all()) if self.rules.exists() else 'No rules'
        return f'Badge {self.title!r} with rules {rules}'

    def has_achievement(self, user: GammaUser) -> bool:
        """
        Check whether badge has any linked achievement via its rules.
        """
        return Achievement.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id
        ).exists()

    @transaction.atomic
    def award_to_user(self, user: GammaUser) -> bool:
        """
        Manually grant this badge to a user, bypassing the event/rules engine.

        Creates a rule-less Achievement for the (user, badge) pair. Because an
        Achievement is considered complete when all of its rules are completed and
        ``all([])`` is ``True``, a rule-less Achievement reads as "earned" everywhere
        the dashboard and leaderboards look. On the first grant only, the badge's
        ``points`` are added to the user's total (and progress timeline) so manually
        awarded badges count toward the general and per-badge leaderboards.

        Return ``True`` if the badge was newly granted, ``False`` if the user already
        had it (idempotent: re-assigning never double-awards points).
        """
        _, created = Achievement.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(type(self)),
            object_id=self.id,
            defaults={
                # Achievement.title is max_length=64 and non-null; Badge.title is 255/nullable.
                'title': (self.title or '')[:64],
                'description': self.description,
                # Manual awards never pass through AchievementCompletionUseCase, so the
                # completion moment (which drives the badge-earned notification) is
                # recorded here at grant time.
                'completed_at': now(),
            },
        )

        if created and self.points:
            user.update_user_points(self.points)
            user.update_user_progress(self.points)

        return created

    @transaction.atomic
    def revoke_from_user(self, user: GammaUser) -> bool:
        """
        Manually remove this badge from a user — the inverse of ``award_to_user``.

        Deletes the user's Achievement for this badge and, if the badge has ``points``,
        reverses them exactly — the inverse of ``award_to_user``'s ``user.points +=
        self.points`` — and reverses the matching progress-timeline entry, keeping the
        general and per-badge leaderboards in sync. The reversal is symmetric with the
        grant regardless of how the badge was originally obtained, so revoking a
        negative-points (penalty) badge restores the docked points, and the total is
        allowed to go below zero.

        Return ``True`` if the badge was removed, ``False`` if the user did not have it
        (idempotent: re-running never deducts points twice).
        """
        achievements = Achievement.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(type(self)),
            object_id=self.id,
        )
        if not achievements.exists():
            return False

        achievements.delete()

        if self.points:
            user.points -= self.points
            user.save(update_fields=('points',))
            user.update_user_progress(-self.points)

        return True

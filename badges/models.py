from django.contrib.contenttypes.fields import ContentType
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now

from achievements.models import Achievement
from badges.exceptions import BadgeExclusionError
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

    excluded_categories = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'Badge categories that disqualify a learner from this badge. If the learner already '
            'holds any badge in any of these categories, granting this one is refused. Example: '
            '["Ignominious!"] stops a learner flagged for gaming completions from being granted '
            'an accomplishment badge.'
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

    def blocking_badges(self, user: GammaUser) -> models.QuerySet:
        """
        Badges the user already holds that disqualify them from this one.

        A badge is disqualifying when its ``category`` appears in this badge's
        ``excluded_categories``. Returns an empty queryset when no exclusions are
        configured, which is the case for every badge by default.
        """
        categories = self.excluded_categories or []
        if not categories:
            return Badge.objects.none()

        held_badge_ids = Achievement.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(type(self)),
        ).values_list('object_id', flat=True)

        return Badge.objects.filter(id__in=held_badge_ids, category__in=categories)

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

        Raise ``BadgeExclusionError`` if the user holds a badge in one of this badge's
        ``excluded_categories``. The check guards the grant here, in the model, so every
        caller is covered rather than only the admin dialog. It runs *after* the
        already-held short-circuit, so a learner who earned this badge before being
        flagged keeps it and re-assignment stays a no-op instead of starting to fail.
        """
        if self.has_achievement(user):
            return False

        blocking = self.blocking_badges(user)
        if blocking.exists():
            raise BadgeExclusionError(self, blocking)

        achievement, created = Achievement.objects.get_or_create(
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
                # Likewise the payment below is recorded here rather than by the
                # completion use case, so a manual grant is auditable the same way.
                'completion_points_paid': self.points or 0,
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

        The amount reversed is what the user was actually *paid*
        (``Achievement.completion_points_paid``), not the badge's current ``points``.
        The two diverge whenever a badge is re-valued after it was earned — which the
        completion-points backfill does deliberately (0 -> N) — and reversing the current
        value would then claw back points the user never received. Achievements predating
        that field have no record, so they fall back to the current value as before.
        """
        achievements = Achievement.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(type(self)),
            object_id=self.id,
        )
        if not achievements.exists():
            return False

        paid = next(
            (a.completion_points_paid for a in achievements if a.completion_points_paid is not None),
            self.points,
        )

        achievements.delete()

        if paid:
            user.points -= paid
            user.save(update_fields=('points',))
            user.update_user_progress(-paid)

        return True


class AntiGamingPenalty(models.Model):
    """
    Per-(learner, course) record of the rushed-"Mark as complete" anti-gaming penalty,
    so the daily ``process_anti_gaming`` detector can apply / adjust / reverse the
    points claw-back idempotently and symmetrically.

    ``points_docked`` is the POSITIVE magnitude currently subtracted from the learner's
    ``GammaUser.points`` for this course (always 0 in ``flag`` mode). On each run the
    detector reconciles the live total by the delta between the freshly-computed target
    dock and this stored value; when the learner stops qualifying (no longer rushing, or
    they have since watched the videos / solved the problems) the record is reversed —
    the docked points are restored — and deleted. ``mode`` mirrors the rule's current
    mode so a flag→dock flip is auditable per learner.
    """

    user = models.ForeignKey(
        GammaUser, on_delete=models.CASCADE, related_name='anti_gaming_penalties',
    )
    course_id = models.CharField(max_length=255)
    points_docked = models.PositiveIntegerField(default=0)
    rushed_blocks = models.PositiveIntegerField(default=0)
    longest_run = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=8, default='flag')
    evaluated_at = models.DateTimeField(default=now)

    class Meta:
        verbose_name = 'Anti-gaming penalty'
        verbose_name_plural = 'Anti-gaming penalties'
        unique_together = ('user', 'course_id')

    def __str__(self):
        return f'AntiGamingPenalty({self.user.user_uid!r}, {self.course_id!r}, -{self.points_docked})'

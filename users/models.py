from datetime import date, datetime
from typing import Dict, List, Optional, Union

from django.db import models
from django.utils.translation import gettext as _

from events.enums import RggInternalEventTypes
from events.models import Event, EventConfiguration
from events.utils import simulate_rgg_internal_event


class GammaUser(models.Model):
    """
    Model represents Gamma User.
    """

    user_uid = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    signup_source = models.CharField(max_length=255, blank=True, null=True)

    # Signed: a manually-assigned negative-points (penalty) badge can dock points and
    # push the total below zero. Per-course points (GammaUserCoursePoints) stay unsigned —
    # manual penalties never touch them.
    points = models.BigIntegerField(default=0)
    chart = models.JSONField(default=dict, blank=True)
    progress = models.JSONField(default=dict, blank=True)

    # When True the user has opted out of leaderboard ranking (Account Settings):
    # they are kept out of every leaderboard (general, course, country, badge) by the
    # building/update pipeline and the ranking endpoints, and evicted from Redis the
    # moment they opt out. Toggled via the leaderboard opt-out API in users/api/v0.
    excluded_from_leaderboard = models.BooleanField(default=False)

    # Continuous Learning streak state (see users.continuous_learning). current_streak is
    # the number of consecutive calendar days the learner has been active (logged in and
    # earning points); last_active_date is the most recent day counted, used to detect
    # whether the next active day continues the run (+1) or breaks it (reset to 1).
    current_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('Gamma User')
        verbose_name_plural = _('Gamma Users')

    def __str__(self):
        return f'Gamma User {self.user_uid!r}'

    @classmethod
    def ensure_gamma_user_is_created(cls, user_uid):
        """
        Ensure that Gamma User exists or create a new one.
        """
        gamma_user, __ = cls.objects.get_or_create(user_uid=user_uid)
        return gamma_user

    def update_user_progress(self, event_points: int, when: Optional[Union[date, datetime]] = None) -> None:
        """
        Update Gamma User progress dict.

        ``when`` overrides the day the points are credited to (defaults to today). It
        lets the Continuous Learning backfill replay historical active days onto their
        real dates; live callers leave it unset and get today's entry as before.
        """
        current_progress = self.progress or {}

        base = when if when is not None else datetime.now()
        if isinstance(base, datetime):
            today_date = base.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            today_date = datetime(base.year, base.month, base.day)
        iso_today_date = today_date.isoformat()
        current_year = str(today_date.year)

        current_progress.setdefault(current_year, [])

        year_entries: List[Dict] = current_progress[current_year]

        today_progress = next((entry for entry in year_entries if entry['date'] == iso_today_date), None)

        if today_progress:
            today_progress['points'] += event_points
        else:
            year_entries.append({
                'date': iso_today_date,
                'points': event_points
            })

        self.progress = current_progress
        self.save(update_fields=('progress',))

    def update_user_chart(self, event_configuration: EventConfiguration) -> None:  # noqa
        """
        Update Gamma User chart dict.
        """
        self.chart = self.chart or {}

        event_chart_key = str(event_configuration.event_type)
        self.chart.setdefault(event_chart_key, {'title': '', 'points': 0})

        self.chart[event_chart_key]['points'] += event_configuration.award
        self.chart[event_chart_key]['title'] = event_configuration.title

        self.save(update_fields=('chart',))

    def add_chart_points(self, key: str, title: str, points: int) -> None:
        """
        Add ``points`` to an arbitrary Points Distribution bucket, keyed by ``key`` and
        labelled ``title``.

        Like ``update_user_chart`` but for points not tied to an EventConfiguration's
        fixed award — used by Continuous Learning, whose daily (5) and streak-bonus
        (10/10/25/50) amounts all accumulate into a single ``continuous_learning`` bucket
        that a one-award-per-type EventConfiguration could not express.
        """
        self.chart = self.chart or {}

        self.chart.setdefault(key, {'title': title, 'points': 0})
        self.chart[key]['points'] += points
        self.chart[key]['title'] = title

        self.save(update_fields=('chart',))

    def update_user_points(self, points: int) -> None:
        """
        Update Gamma User points.
        """
        self.points += points
        self.save(update_fields=('points',))

    def update_user_course_points(self, event: Event) -> None:
        """
        Update Gamma User points earned for the course.
        """
        if not (event_course_id := event.course_id):
            return

        event_configuration = event.configuration
        event_award = event_configuration.award

        user_course_points, created = GammaUserCoursePoints.objects.get_or_create(
            gamma_user=self,
            course_id=event_course_id,
            defaults={'points': event_award},
        )

        if not created:
            user_course_points.points += event_award
            user_course_points.save(update_fields=('points',))

    def run_update_user_pipeline(self, event: Event) -> None:
        """
        Aggregated pipeline with actions which updates user progress.
        """
        event_configuration = event.configuration

        self.update_user_progress(event_configuration.award)
        self.update_user_chart(event_configuration)
        self.update_user_points(event_configuration.award)
        self.update_user_course_points(event)
        simulate_rgg_internal_event(self, RggInternalEventTypes.RGG_POINTS_DISTRIBUTION.value)


class GammaUserCoursePoints(models.Model):
    """
    Represent points earned by the user for the course.
    """

    gamma_user = models.ForeignKey(GammaUser, on_delete=models.CASCADE, related_name='courses_points')
    course_id = models.CharField(max_length=255)
    points = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = _('Gamma User course points')
        verbose_name_plural = _("Gamma User courses' points")
        unique_together = ('gamma_user', 'course_id')

    def __str__(self) -> str:
        return f'{self.gamma_user.user_uid}: {self.course_id} - {self.points} points'

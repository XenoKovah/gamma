from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _

from events.models import Event, EventConfiguration


class GammaUser(models.Model):
    """
    Model represents Gamma User.
    """

    user_uid = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    signup_source = models.CharField(max_length=255, blank=True, null=True)

    points = models.PositiveBigIntegerField(default=0)
    chart = models.JSONField(default=dict, blank=True)
    progress = models.JSONField(default=dict, blank=True)

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

    def update_user_progress(self, event_points: int) -> None:
        """
        Update Gamma User progress dict.
        """
        current_progress = self.progress or {}

        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        year = str(date.year)
        formatted_date = date.strftime('%Y.%m.%d')

        points_key = f'progress.{year}.points'
        points_by_day_key = f'progress.{year}'

        if points_key not in current_progress:
            current_progress[points_key] = 0

        if points_by_day_key not in current_progress:
            current_progress[points_by_day_key] = {}

        if formatted_date not in current_progress[points_by_day_key]:
            current_progress[points_by_day_key][formatted_date] = 0

        current_progress[points_key] += event_points
        current_progress[points_by_day_key][formatted_date] += event_points

        self.progress = current_progress
        self.save(update_fields=('progress',))

    def update_user_chart(self, event_configuration: EventConfiguration) -> None:  # noqa
        """
        Update Gamma User chart dict.
        """
        self.chart = self.chart or {}

        event_chart_key = f'chart.{event_configuration.event_type}'
        self.chart.setdefault(event_chart_key, {'title': '', 'points': 0})

        self.chart[event_chart_key]['points'] += event_configuration.award
        self.chart[event_chart_key]['title'] = event_configuration.title

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

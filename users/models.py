from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _

from events.models import EventConfiguration


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

    def run_update_user_pipeline(self, event_configuration: EventConfiguration) -> None:
        """
        Aggregated pipeline with actions which updates user progress.
        """
        self.update_user_progress(event_configuration.award)
        self.update_user_chart(event_configuration)
        self.update_user_points(event_configuration.award)

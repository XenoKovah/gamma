from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _


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
        return f'Gamma User {self.username}'

    @classmethod
    def update_user_progress(cls, username: str, event_points: int) -> None:
        """
        Update Gamma User progress dict.
        """
        user = cls.objects.get(username=username)
        current_progress = user.progress or {}

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

        user.progress = current_progress
        user.save(update_fields=['progress'])

    @classmethod
    def update_user_chart(cls, username: str, event: "Event") -> None:  # noqa
        """
        Update Gamma User chart dict.
        """
        user = cls.objects.get(username=username)
        user.chart = user.chart or {}

        event_chart_key = f'chart.{event.configuration.event_type}'
        user.chart.setdefault(event_chart_key, {'title': '', 'points': 0})

        user.chart[event_chart_key]['points'] += event.configuration.award
        user.chart[event_chart_key]['title'] = event.configuration.title

        user.save(update_fields=['chart'])

    @classmethod
    def update_user_points(cls, username: str, points: int) -> None:
        """
        Update Gamma User points.
        """
        user = cls.objects.get(username=username)
        user.points += points
        user.save(update_fields=['points'])

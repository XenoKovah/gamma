""" API v0 paths. """
from django.urls import path

from .views import (
    ProgressView,
    ChartView,
    PointsView,
    GameProfileView,
    BadgesView,
    EventPointsView,
    StatusView,
    LoggedEventView,
    ApiAccessEventView,
)


urlpatterns = [
    path(r'progress/', ProgressView.as_view(), name='progress'),
    path(r'chart/', ChartView.as_view(), name='chart'),
    path(r'points/', PointsView.as_view(), name='points'),
    path(r'gamma-profile/', GameProfileView.as_view(), name='gamma-profile'),
    path(r'badges/', BadgesView.as_view(), name='badges'),
    path(r'statuses/', StatusView.as_view(), name='statuses'),
    path(r'event-points/', EventPointsView.as_view(), name='event-points'),
    path(r'logged-event/', LoggedEventView.as_view(), name='logged-event'),
    path(r'api-access/', ApiAccessEventView.as_view(), name='api-access'),
]

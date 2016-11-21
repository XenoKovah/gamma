""" API v0 URLs. """
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProgressView,
    ChartView,
    PointsView,
    GameProfileView,
    BadgesView,
    EventPointsView,
    StatusView,
    LoggedEventView,
)


urlpatterns = [
    url(r'^progress/*$', ProgressView.as_view(), name='progress'),
    url(r'^chart/*$', ChartView.as_view(), name='chart'),
    url(r'^points/*$', PointsView.as_view(), name='points'),
    url(r'^gamma-profile/*$', GameProfileView.as_view(), name='gamma-profile'),
    url(r'^badges/*$', BadgesView.as_view(), name='badges'),
    url(r'^statuses/*$', StatusView.as_view(), name='statuses'),
    url(r'^event-points/*$', EventPointsView.as_view(), name='event-points'),
    url(r'^logged-event/*$', LoggedEventView.as_view(), name='logged-event'),
]

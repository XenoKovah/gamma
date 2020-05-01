""" API v0 paths. """
from django.urls import path

from .views import (
    ProgressView,
    ChartView,
    PointsView,
    GameProfileView,
    BadgesView,
    StatusView,
    UserStatuses,
    ActionsListView,
    BadgesListView,
    StatusBadgesListView,
    FiltersView,
    BadgeRulesView,
    CoursesView,
    OrganizationsView,
    AchievementsView,
    LeaderBoardView
)


urlpatterns = [
    path(r'progress/', ProgressView.as_view(), name='progress'),
    path(r'chart/', ChartView.as_view(), name='chart'),
    path(r'points/', PointsView.as_view(), name='points'),
    path(r'gamma-profile/', GameProfileView.as_view(), name='gamma-profile'),
    path(r'badges/', BadgesView.as_view(), name='badges'),
    path(r'user-statuses/', UserStatuses.as_view(), name='user-statuses'),
    path(r'statuses/', StatusView.as_view(), name='statuses'),
    path(r'actions/', ActionsListView.as_view(), name='actions'),
    path(r'badges-list/', BadgesListView.as_view(), name='badges-list'),
    path(r'status-badges-list/', StatusBadgesListView.as_view(), name='status-badges-list'),
    path(r'filters/', FiltersView.as_view(), name='filters'),
    path(r'badge-rules/', BadgeRulesView.as_view(), name='badge-rules'),
    path(r'courses/', CoursesView.as_view(), name='courses'),
    path(r'organizations/', OrganizationsView.as_view(), name='organizations'),
    path(r'achievements/', AchievementsView.as_view(), name='achievements'),
    path(r'leaderboard/', LeaderBoardView.as_view(), name='leaderboard'),
]

"""API v0 paths."""
from django.urls import path

from .views import (
    GameProfileView,
    ActionsListView,
    BadgesView,
    StatusBadgesView,
    FiltersView,
    BadgeRulesView,
    CoursesView,
    OrganizationsView,
    AchievementsView,
    LeaderBoardView,
    BadgeDependentBadgesView,
    StatusDependentBadgesView,
    SignupSourceUpdateView
)


urlpatterns = [
    path(r'gamma-profile/', GameProfileView.as_view(), name='gamma-profile'),
    path(r'actions/', ActionsListView.as_view(), name='actions'),
    path(r'badges-list/', BadgesView.as_view(), name='badges-list'),
    path(r'status-badges-list/', StatusBadgesView.as_view(), name='status-badges-list'),
    path(r'filters/', FiltersView.as_view(), name='filters'),
    path(r'badge-rules/', BadgeRulesView.as_view(), name='badge-rules'),
    path(r'courses/', CoursesView.as_view(), name='courses'),
    path(r'organizations/', OrganizationsView.as_view(), name='organizations'),
    path(r'achievements/', AchievementsView.as_view(), name='achievements'),
    path(r'leaderboard/', LeaderBoardView.as_view(), name='leaderboard'),
    path(r'badge-dependent-badges-list/', BadgeDependentBadgesView.as_view(), name='badge-dependent-badges-list'),
    path(r'status-dependent-badges-list/', StatusDependentBadgesView.as_view(), name='status-dependent-badges-list'),
    path(r'update_profile_signup_source/', SignupSourceUpdateView.as_view(), name='update-profile-signup-source'),
]

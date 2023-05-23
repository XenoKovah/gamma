"""API v1 paths."""
from django.urls import path

from .views import (
    LeaderBoardView,
)


urlpatterns = [
    path(r'leaderboard/', LeaderBoardView.as_view(), name='leaderboard'),
]

from django.urls import path

from leaderboard.api.v0.views import BadgeLeaderBoardView, LeaderBoardView


urlpatterns = [
    path("leaderboard", LeaderBoardView.as_view(), name="leaderboard"),
    path("leaderboard/badge/<slug:badge_slug>", BadgeLeaderBoardView.as_view(), name="badge-leaderboard"),
]

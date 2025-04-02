from django.urls import path

from leaderboard.api.v0.views import LeaderBoardView


urlpatterns = [
    path("leaderboard", LeaderBoardView.as_view(), name="leaderboard"),
]

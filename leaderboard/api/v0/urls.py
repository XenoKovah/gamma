from django.urls import path

from leaderboard.api.v0.views import BadgeLeaderBoardView, CoursePointsView, LeaderBoardView


urlpatterns = [
    path("leaderboard", LeaderBoardView.as_view(), name="leaderboard"),
    path("leaderboard/badge/<slug:badge_slug>", BadgeLeaderBoardView.as_view(), name="badge-leaderboard"),
    path("course-points", CoursePointsView.as_view(), name="course-points"),
]

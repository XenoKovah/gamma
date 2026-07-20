from django.urls import path

from leaderboard.api.v0.views import (
    BadgeLeaderBoardView,
    CoursePointsView,
    InstructorUserUidsView,
    LeaderBoardView,
    UsersLeaderBoardView,
)


urlpatterns = [
    path("leaderboard", LeaderBoardView.as_view(), name="leaderboard"),
    path("leaderboard/badge/<slug:badge_slug>", BadgeLeaderBoardView.as_view(), name="badge-leaderboard"),
    path("leaderboard/users", UsersLeaderBoardView.as_view(), name="users-leaderboard"),
    path("leaderboard/instructor-uids", InstructorUserUidsView.as_view(), name="leaderboard-instructor-uids"),
    path("course-points", CoursePointsView.as_view(), name="course-points"),
]

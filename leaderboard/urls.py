from django.urls import path, include

urlpatterns = [
    path("v0/", include("leaderboard.api.v0.urls")),
]

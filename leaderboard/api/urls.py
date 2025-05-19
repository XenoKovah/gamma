from django.urls import include, path

urlpatterns = [
    path('v0/', include(('leaderboard.api.v0.urls', 'leaderboard'),  namespace='v0')),
]

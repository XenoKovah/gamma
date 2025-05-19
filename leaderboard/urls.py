from django.urls import include, path


app_name = 'leaderboard'
urlpatterns = [
    path('api/', include(('leaderboard.api.urls', 'leaderboard'), namespace='api')),
]

from django.urls import include, path


app_name = 'badges'
urlpatterns = [
    path('api/', include(('badges.api.urls', 'badges'), namespace='api')),
]

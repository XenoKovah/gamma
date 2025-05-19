from django.urls import include, path


app_name = 'avatars'
urlpatterns = [
    path('api/', include(('avatars.api.urls', 'avatars'), namespace='api')),
]

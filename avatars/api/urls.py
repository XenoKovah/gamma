from django.urls import include, path


urlpatterns = [
    path('v0/', include(('avatars.api.v0.urls', 'avatars'),  namespace='v0')),
]

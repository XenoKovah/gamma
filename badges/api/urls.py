from django.urls import include, path


urlpatterns = [
    path('v0/', include(('badges.api.v0.urls', 'badges'),  namespace='v0')),
]

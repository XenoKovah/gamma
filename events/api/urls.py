from django.urls import include, path


urlpatterns = [
    path('v0/', include(('events.api.v0.urls', 'events'),  namespace='v0')),
]

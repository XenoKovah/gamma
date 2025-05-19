from django.urls import include, path

app_name = 'events'
urlpatterns = [
    path('api/', include(('events.api.urls', 'events'), namespace='api')),
]

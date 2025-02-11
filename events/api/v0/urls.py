from django.urls import path

from events.api.v0.views import EventsAPIView

urlpatterns = [
    path('events/', EventsAPIView.as_view(), name='events'),
]

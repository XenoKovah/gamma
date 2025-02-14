from django.urls import path

from .views import AvailableActionsAPIView, EventsAPIView

urlpatterns = [
    path('events/', EventsAPIView.as_view(), name='events'),
    path('available-actions/', AvailableActionsAPIView.as_view(), name='available-actions'),
]

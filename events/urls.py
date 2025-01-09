from django.urls import path
from events.views import PutEventView

urlpatterns = [
    path('events/create/', PutEventView.as_view(), name='put_event'),
]

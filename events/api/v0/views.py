from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils

from events.models import EventConfiguration

from .serializers import AvailableActionsSerializer, EventSerializer


class EventsAPIView(APIView, AppClientUtils):
    """
    API endpoint to handle event creation.

    Body params:
        - event_type (string): The type of incoming event. Must exists as valid event type.
        - username (string): The unique identifier of the user associated with the event.
        - signup_source (string): The source from which the user signed up (e.g., "main", "host.com").
        - course_id (string): The course id associated with the event.
        - org (string): The organization of the course.
        - uid (string): A unique identifier for the event.
        - event (dict): Detailed event data for course.
        - context (dict): Metadata about the event request.
        - full_event (dict): Detailed event data including session, IP address, user agent.

    Example Response:
        {
            "uid": "ea78013dc424f12c796570640bd431d25d1007eq",
            "signup_source": "main",
            "username": "openedx",
            "created_at": "2025-01-13T19:33:20.279680Z",
            "client": "main",
            "org": "edx",
            "course_id": "course-v1:edx+101+101",
            "configuration": {
                "event_type": "edx_bookmark_added",
                "title": "Bookmark added",
                "award": 10,
                "color": 1,
                "notification_message": "You have got {} point."
            }
        }

    Returns:
        - HTTP 201 Created: If the event is successfully created.
        - HTTP 400 Bad Request: If the input data fails validation.
    """

    authentication_classes = (KeySecretAuthentication,)
    serializer_class = EventSerializer

    def post(self, request, *args, **kwargs):
        data = self.update_data_with_client_uid()

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AvailableActionsAPIView(generics.ListAPIView):
    """
    API endpoint to show all configured event types.
    """

    model = EventConfiguration
    serializer_class = AvailableActionsSerializer
    queryset = EventConfiguration.objects.all()

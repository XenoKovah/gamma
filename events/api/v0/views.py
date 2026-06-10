from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.authentication import KeySecretAuthentication

from events.constants import TEMPORALLY_EXCLUDED_EVENT_TYPES
from events.models import Event, EventConfiguration

from .serializers import AvailableActionsSerializer, EventSerializer


class EventsAPIView(APIView):
    """
    API endpoint to handle event creation.

    Body params:
        - event_type (string): The type of incoming event. Must exists as valid event type.
        - username (string): The unique identifier of the user associated with the event.
        - signup_source (string): The source from which the user signed up (e.g., "main", "host.com").
        - course_id (string): The course id associated with the event.
        - org (string): The organization of the course.
        - block_id (string): The usage key of the block the event concerns, if any.
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
                "award": 10
            }
        }

    Returns:
        - HTTP 201 Created: If the event is successfully created.
        - HTTP 400 Bad Request: If the input data fails validation.
    """

    authentication_classes = (KeySecretAuthentication,)
    serializer_class = EventSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update({'client': request.client.name})

        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            self._record_block_id_on_duplicate(data, serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _record_block_id_on_duplicate(data, errors):
        """
        Teach a pre-existing row its block when a duplicate arrives.

        Events ingested before ``Event.block_id`` existed have a NULL block_id, and
        the uid (a hash that includes the block) cannot be reversed to recover it.
        When the same logical event is re-sent (e.g. by the done-state backfill) and
        collides on the (uid, client, username) uniqueness, copy the incoming
        block_id onto the stored row so block-filtered rules count it on the next
        recompute. The duplicate itself is still rejected with the usual 400.
        """
        is_duplicate = any('unique set' in str(error) for error in errors.get('non_field_errors', ()))
        if not (is_duplicate and data.get('block_id')):
            return

        Event.objects.filter(
            uid=data.get('uid'),
            client=data.get('client'),
            username=data.get('username'),
            block_id__isnull=True,
        ).update(block_id=data['block_id'])


class AvailableActionsAPIView(generics.ListAPIView):
    """
    API endpoint to show all configured event types.
    """

    model = EventConfiguration
    serializer_class = AvailableActionsSerializer

    def get_queryset(self):
        """
        Returns a queryset of EventConfiguration objects, excluding Event Types
        which is in TEMPORALLY_EXCLUDED_EVENT_TYPES.
        """
        return EventConfiguration.objects.exclude(event_type__name__in=TEMPORALLY_EXCLUDED_EVENT_TYPES)

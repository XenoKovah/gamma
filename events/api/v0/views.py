from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.enums import AchievementTypes
from core.authentication import KeySecretAuthentication
from events.models import EventConfiguration
from events.services import get_event_configuration_service

from .serializers import AvailableActionsSerializer, EventSerializer

EVENTS_API_TAG = 'Events'


class EventsAPIView(APIView):
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
                "award": 10
            }
        }

    Returns:
        - HTTP 201 Created: If the event is successfully created.
        - HTTP 400 Bad Request: If the input data fails validation.
    """

    authentication_classes = (KeySecretAuthentication,)
    serializer_class = EventSerializer

    @swagger_auto_schema(
        tags=[EVENTS_API_TAG],
        operation_summary='Create an event',
        operation_description='Create an Event record from incoming event payloads.',
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update({'client': request.client.name})

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        tags=[EVENTS_API_TAG],
        operation_summary='List available event actions',
        operation_description=(
            'Return EventConfiguration objects, optionally filtered by `achievement_type` query parameter.'
        ),
        manual_parameters=[
            openapi.Parameter(
                'achievement_type',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                enum=AchievementTypes.get_all(),
            )
        ],
        responses={200: openapi.Response('OK', AvailableActionsSerializer(many=True))}
    ),
)
class AvailableActionsAPIView(generics.ListAPIView):
    """
    API endpoint to show all configured event types.
    """

    model = EventConfiguration
    serializer_class = AvailableActionsSerializer

    def get_queryset(self) -> QuerySet[EventConfiguration]:
        """
        Return available actions based on EventConfiguration.

        If 'achievement_type' query param is provided, filter configurations accordingly.
        """
        achievement_type = self.request.query_params.get('achievement_type')
        if not achievement_type:
            return get_event_configuration_service().get_available()

        try:
            achievement_type = AchievementTypes.from_value(achievement_type)
        except ValueError:
            return EventConfiguration.objects.none()

        return get_event_configuration_service(achievement_type).get_available()

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


from core.db.engine import conn
from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils

from events.exceptions import (
    EventDataIsNotCorrectError,
    EventTypeIsNotRecognizableError,
    DuplicatedEventOccursError,
)
from events.usecases import ProcessIncomingEventUseCase
from events.repository import EventRepository
from schematics.exceptions import DataError


from events.serializers import EventSerializer


class PutEventView(APIView, AppClientUtils):
    """

    """

    authentication_classes = (KeySecretAuthentication,)
    serializer_class = EventSerializer

    def put(self, request, *args, **kwargs):
        data = self.update_data_with_client_uid()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(rais_exteption=True)

        event = serializer.save()
        return Response(self.get_serializer(event).data, status=status.HTTP_201_CREATED)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core import db
from core.db.engine import conn
from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils
from events.usecases import GetEventsUseCase
from events.repository import EventRepository
from users.api.v0.serializers import UserGameProfileSerializer


class UserGameProfileView(APIView, AppClientUtils):
    """
    User's Game Profile API view.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({'Error': 'user_uid must be set'}, status=status.HTTP_400_BAD_REQUEST)

        user = db.users.read_one(user_uid)
        user.system_statuses = db.statuses.read()

        repository = EventRepository(conn.db)
        user.system_events = GetEventsUseCase(repository).execute()

        user_data = user.to_primitive('public')

        serializer = UserGameProfileSerializer(data={}, context={'user_uid': user_uid})
        serializer.is_valid()
        user_data.update(serializer.data)

        return Response(user_data)

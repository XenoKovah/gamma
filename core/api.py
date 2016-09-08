from datetime import datetime, timedelta

from pymongo import MongoClient
from django.contrib.auth.models import User
from django.db.models import F
from django.conf import settings
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from .models import GameProfile
from .serializers import GameProfileSerializer, ProgressSerializer
from .utils import find_one_and_update, get_progress
from .authentication import KeySecretAuthentication

from pointlog.models import LoggedEvent
from pointlog.tasks import check_user_achievements


CLIENT = client = MongoClient(
    settings.MONGODB_CONF.get('HOST', 'localhost'),
    settings.MONGODB_CONF.get('PORT', 27017),
)
DB = CLIENT[settings.MONGO_DB_NAME]

username = settings.MONGODB_CONF.get('USERNAME')
password = settings.MONGODB_CONF.get('PASSWORD')

if username and password:
    DB.authenticate(
        username, password, source=settings.MONGO_DB_NAME
    )


class GameProfileView(APIView):
    """
    GET or UPDATE user points.
    """
    authentication_classes = (KeySecretAuthentication,)

    def put(self, request, *args, **kwargs):
        """
        Update User GameProfile info.

        Request example:
        http://localhost/gamma-profile/
        {
          "username": :username
          "event_type": :type
        }

        where :username - username for User to update points
              :type - can be `video`, `unit` or `course`
        """
        try:
            user = User.objects.get(username=request.data.get('username'))
        except User.DoesNotExist:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        game_profile = GameProfile.objects.get(user=user)
        event_type = self.request.data.get('event_type')
        uniq_id = self.request.data.get('uid')

        if not uniq_id:
            return Response(
                {"Error": "UID field is mandatory"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        if not LoggedEvent.objects.filter(
            uniq_id=uniq_id,
            user=user,
            event_type=event_type,
            client=request.client
        ).exists():
            points_settings = DB[settings.MONGO_SETTINGS_COLLECTION]
            points_map = points_settings.find_one()
            points_to_update = points_map.get(event_type, 0)
            game_profile.points = F('points') + points_to_update
            # TODO try to avoid duplicate saving in Serializer
            game_profile.save()
            # Update point value in mongo
            find_one_and_update(
                filter_dict={
                    'date': datetime.strptime(
                        str(datetime.now().date()), '%Y-%m-%d'
                    ),
                    'username': user.username
                },
                key='points',
                value=points_to_update
            )
            game_profile = GameProfile.objects.get(user=user)
            serializer = GameProfileSerializer(game_profile)

            # Logging this event to prevent repeating
            log_event = LoggedEvent(
                uniq_id=uniq_id,
                user=user,
                event_type=event_type,
                points=game_profile.points,
                client=request.client
            )
            log_event.save()

            # emit celery task to check for achivement
            check_user_achievements.apply_async(
                (user.id, event_type), countdown=30
            )
            return Response(serializer.data)
        else:
            return Response(
                {"Error": "Repeated event occurs"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.get(username=request.data.get('username'))
        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile)

        return Response(serializer.data)


class ProgressView(APIView):
    """
    Retrieve User progress.
    """
    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.get(username=request.data.get('username'))
        progress_data = get_progress(user)
        serializer = ProgressSerializer(progress_data, many=True)

        return Response(serializer.data)

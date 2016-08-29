from datetime import datetime, timedelta

from pymongo import MongoClient
from django.contrib.auth.models import User
from django.db.models import F
from django.conf import settings
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from .models import GameProfile
from .serializers import GameProfileSerializer, ProgressSerializer
from .utils import find_one_and_update, get_progress


CLIENT = MongoClient()
DB = CLIENT[settings.MONGO_DB_NAME]


class GameProfileView(generics.RetrieveUpdateAPIView, viewsets.GenericViewSet):
    """
    GET or UPDATE user points.
    """
    parser_classes = (JSONParser,)
    serializer_class = GameProfileSerializer

    def update(self, request, *args, **kwargs):
        """
        Update User GameProfile info.

        Request example:
        http://localhost/game-profile/:id/
        {
          "event_type": :type
        }

        where :id - user id
              :type - can be `video`, `unit` or `course`
        """
        user = User.objects.get(id=kwargs.get('pk'))
        game_profile = GameProfile.objects.get(user=user)
        event_type = self.request.data.get('event_type')
        points_settings = DB[settings.MONGO_SETTINGS_COLLECTION]
        points_map = points_settings.find_one()
        points_to_update = points_map.get(event_type, 0)
        game_profile.points = F('points') + points_to_update
        # TODO try to avoid duplicate saving in Serializer
        game_profile.save()
        # Update point value in mongo
        find_one_and_update(
            filter_dict={
                'date': datetime.strptime(str(datetime.now().date()), '%Y-%m-%d'),
                'username': user.username
            },
            key='points',
            value=points_to_update
        )
        game_profile = GameProfile.objects.get(user=user)
        serializer = self.get_serializer(game_profile)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.get(id=kwargs.get('pk'))
        game_profile = GameProfile.objects.get(user=user)
        serializer = self.get_serializer(game_profile)
        return Response(serializer.data)


class ProgressView(APIView):
    """
    Retrieve User progress.
    """
    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.get(id=kwargs.get('pk'))
        progress_data = get_progress(user)
        serializer = ProgressSerializer(progress_data, many=True)
        return Response(serializer.data)

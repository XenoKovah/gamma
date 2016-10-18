from datetime import datetime

from pymongo import MongoClient
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.conf import settings
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from ..forms import EventPointsForm
from ..serializers import (
    GameProfileSerializer,
    ProgressSerializer,
    BadgesSerializer,
)

from core.services import MongoConnector
from core.authentication import KeySecretAuthentication
from core.models import GameProfile, Event
from pointlog.models import LoggedEvent
from pointlog.tasks import check_user_achievements
from achievements.models import UserAchievement


class GameProfileView(APIView):
    """
    GET or UPDATE user points.
    """
    authentication_classes = (KeySecretAuthentication,)

    conn = MongoConnector()

    def put(self, request, *args, **kwargs):
        """
        Update User GameProfile info.

        Request example:
        http://localhost/api/v0/gamma-profile/
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
            # Creating User instance
            # In a future user can login with SSO
            # Need to test it
            user = User(username=request.data.get('username'))
            user.save()
        game_profile = GameProfile.objects.get(user=user)
        event_type = self.request.data.get('event_type')
        uniq_id = self.request.data.get('uid')

        if not uniq_id:
            return Response(
                {"Error": "UID field is mandatory"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        # TODO think about uniq_together and event_type
        if not LoggedEvent.objects.filter(
            uniq_id=uniq_id,
            user=user,
            event_type=event_type,
            client=request.client
        ).exists():
            event = Event.objects.filter(event_type=event_type).first()
            if event and event.award:
                game_profile.points = F('points') + event.award
                # TODO try to avoid duplicate saving in Serializer
                game_profile.save()

                # TODO move this action to Celery
                # Update point value in mongo
                self.conn.find_one_and_update(
                    filter_dict={
                        'date': datetime.strptime(
                            str(datetime.now().date()), '%Y-%m-%d'
                        ),
                        'username': user.username
                    },
                    key='points',
                    value=event.award
                )
                # TODO refactor this
                self.conn.find_one_and_update(
                    filter_dict={
                        'username': user.username
                    },
                    key=event_type,
                    value=event.award,
                    event_type='chart'
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

                check_user_achievements(user.id, event_type)
                return Response(serializer.data)
            else:
                return Response(
                    {"Error": "Event type is not recognizable"},
                    status.HTTP_406_NOT_ACCEPTABLE
                )
        else:
            return Response(
                {"Error": "Repeated event occurs"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.filter(username=request.data.get('username')).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile)

        return Response(serializer.data)


class ProgressView(APIView):
    """
    Retrieve User progress.
    """
    conn = MongoConnector()

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.filter(username=request.GET.get('username')).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        progress_data = self.conn.get_progress(user)
        serializer = ProgressSerializer(progress_data, many=True)
        data = serializer.data
        # TODO reverse on Mongo side
        data.reverse()

        return Response(data)


class EventPointsView(APIView):
    """
    API to reward particular User with points.
    """
    def post(self, request, *args, **kwargs):
        form = EventPointsForm(request.POST)
        if form.is_valid():
            form.save_event_points()
            return Response({
                'username': form.cleaned_data['username'],
                'points': form.cleaned_data['points']
            })
        else:
            return Response(
                {'msg': "Requested reward is not valid."}, status=401
            )


class ChartView(APIView):
    """
    Retrieve User chart.
    """
    conn = MongoConnector()

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user chart data.
        """
        user = User.objects.filter(username=request.GET.get('username')).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        progress_data = self.conn.get_charted_progress(user)

        return Response(progress_data)


class PointsView(APIView):
    """
    Retrieve User game profile.

    If User DoesNotExist - return zero points.
    """
    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        user = User.objects.filter(username=request.GET.get('username')).first()
        if not user:
            return Response(
                {"username": request.GET.get('username'), "points": 0}
            )
        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile)

        return Response(serializer.data)


class BadgesView(APIView):
    """
    Badges API.
    """
    def get(self, request, *args, **kwargs):
        """
        Get badges for particular User.

        If UserNotFount - return status 404 w/ msg User not found.
        """
        user = User.objects.filter(
            username=request.GET.get('username')
        ).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        badges = (
            achive.achievement for achive in
            UserAchievement.objects.filter(user=user)
        )
        serializer = BadgesSerializer(
            badges, context={'request': request}, many=True
        )
        return Response(serializer.data)

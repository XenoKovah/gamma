import logging
from datetime import datetime, timedelta

import pymongo
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
    LoggedEventSerializer,
    ApiAccessEventSerializer,
    UserStatusSerializer,
    EventSerializer
)

from core.services import MongoConnector
from core.authentication import KeySecretAuthentication
from core.models import GameProfile, AppClient
from core.mongo import c_badges
from achievements.services import AchievementRulesMongo
from pointlog.models import LoggedEvent
from pointlog.models import ApiAccessEvent
from pointlog.tasks import check_user_achievements, assign_status
from achievements.models import UserAchievement, Achievement, StatusBadge, Event, UserStatus


logger = logging.getLogger('events')


class GameProfileView(APIView):
    """
    GET or UPDATE user points.
    """

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
        org = self.request.data.get('org', 'org')
        uniq_id = self.request.data.get('uid')

        if not uniq_id:
            logger.debug('For user {0} msg: {1} event_type=>{2}'.format(
                user.username, 'UID field is mandatory', event_type
            ))
            return Response(
                {"Error": "UID field is mandatory"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        # TODO think about uniq_together and event_type
        if not LoggedEvent.objects.filter(
            uniq_id=uniq_id,
            user=user,
            event_type=event_type,
            client=AppClient.objects.get(id=1)
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
                    org=org,
                    points=game_profile.points,
                    client=AppClient.objects.get(id=1),
                    rewarded_points=event.award
                )
                log_event.save()
                logger.debug('For user {0} msg: {1}'.format(
                    user.username,
                    'Event logged::uniq_id=>{0}::event_type=>{1}::points=>{2}'.format(
                        uniq_id, event_type, event.award
                    )
                ))
                check_user_achievements(user.id, log_event)
                assign_status(user.id, game_profile.points)
                return Response(serializer.data)
            else:
                logger.debug('For user {0} msg: {1}: {2}'.format(
                    user.username,
                    'Event type is not recognizable',
                    event_type
                ))
                return Response(
                    {"Error": "Event type is not recognizable"},
                    status.HTTP_406_NOT_ACCEPTABLE
                )
        else:
            logger.debug('For user {0} msg: {1}: {2}::{3}'.format(
                user.username,
                'Repeated event occurs',
                event_type, uniq_id
            ))
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
        form = EventPointsForm(request.data)
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
        data = {}
        for key in progress_data:
            event_title, order = Event.objects.values_list(
                'title', 'color'
            ).filter(event_type=key).first()
            if event_title:
                data[event_title] = (order, progress_data[key])
            else:
                data[key] = (order, progress_data[key])
        log_api_access = ApiAccessEvent(
            user=user,
            api_name='Charts'
        )
        log_api_access.save()

        return Response(data)


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

        conn = AchievementRulesMongo()
        conn.connect()
        badges = conn.collection.find({"active": True})
        for badge in badges:
            c_badges().update(
                {"user_id": user.id},
                {
                    "$set": {
                        "badges.{}".format(badge.get("slug")): badge.get("users", {}).get(str(user.id), {})
                    }
                },
                upsert=True
            )

            rule = badge.get("users", {}).get(str(user.id), {})
            done = all(
                map(
                    lambda x: x[0] >= x[1],
                    (
                        (rule[i].get('count'), badge.get("rules", {}).get("actions", {}).get(i))
                        for i in rule if not i == 'done')
                )
            ) if rule else False

            c_badges().update(
                {"user_id": user.id},
                {
                    "$set": {
                        "badges.{}.done".format(badge.get("slug")): done
                    }
                },
            )

        log_api_access = ApiAccessEvent(
            user=user,
            api_name='Badges'
        )
        log_api_access.save()

        return Response(c_badges().find_one({"user_id": user.id}, {"_id": 0}).get('badges'))


class UserStatuses(APIView):
    """
    Return achieved statuses.
    """
    def get(self, request, *args, **kwargs):
        """
        Get user's statuses.
        """
        user = User.objects.filter(
            username=request.GET.get('username')
        ).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        user_statuses = UserStatus.objects.filter(user=user)
        serializer = UserStatusSerializer(
            [i.status for i in user_statuses], context={'request': request}, many=True
        )

        return Response(serializer.data)


class StatusView(APIView):
    """
    Statuses API.
    """
    def get(self, request, *args, **kwargs):
        """
        Get configured statuses.
        """
        statuses = StatusBadge.objects.filter()
        serializer = UserStatusSerializer(
            statuses, context={'request': request}, many=True
        )

        return Response(serializer.data)


class LoggedEventView(APIView):
    """
    Return all new Events for user.

    Computed based on request time.
    """
    def get(self, request, *args, **kwargs):
        """
        Get latest LoggedEvents.
        """
        user = User.objects.filter(
            username=request.GET.get('username')
        ).first()
        if not user:
            return Response(
                {"Error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        qs = LoggedEvent.objects.filter(
            user=user, date__gte=datetime.now()-timedelta(minutes=5)
        )
        serializer = LoggedEventSerializer(qs, many=True)
        return Response(serializer.data)


class ApiAccessEventView(APIView):
    """
    Return all new Events for user.

    Computed based on request time.
    """
    def get(self, request, *args, **kwargs):
        """
        Get latest LoggedEvents.
        """
        qs = ApiAccessEvent.objects.all()
        serializer = ApiAccessEventSerializer(qs, many=True)
        return Response(serializer.data)


class EventsView(APIView):
    """
    Return all available Events.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all Events.
        """
        qs = Event.objects.all()
        serializer = EventSerializer(qs, many=True)
        return Response(serializer.data)


class FiltersView(APIView):
    """
    Return all available Filters.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all Filters.
        """
        return Response([
            {'org': 'String'},
            {'interval': {'start': 'Date', 'end': 'Date'}},
            {'frequency': 'Int32'}])


class BadgeRuleView(APIView):
    """
    Return Badge rules.
    """
    conn = AchievementRulesMongo()
    conn.connect()

    def get(self, request, *args, **kwargs):
        """
        Get rules for badge by a slug.
        """
        slug = request.GET.get('slug')
        if not slug:
            return Response({})
        badge = self.conn.collection.find_one({"slug": slug}, {"_id": 0})
        print(badge)
        return Response(badge.get('rules', {}) if badge else {})

    
    def put(self, request, *args, **kwargs):
        print(request.data)
        return Response({}, status=200)

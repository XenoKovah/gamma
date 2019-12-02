import logging
from collections import OrderedDict
from datetime import datetime, timedelta

import http.client
import os

import pymongo
from pymongo import MongoClient
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from edx_integration.api.v2.client import EdxApiV2Client
from edx_integration.api.v2.exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)

from ..forms import EventPointsForm
from ..serializers import (
    GameProfileSerializer,
    ProgressSerializer,
    BadgesSerializer,
    LoggedEventSerializer,
    ApiAccessEventSerializer,
    UserStatusSerializer,
    StatusSerializer,
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
from achievements.forms import AchievementForm


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
logger = logging.getLogger('events')


class GameProfileView(APIView):
    """
    GET or UPDATE user points.
    """

    conn = MongoConnector()
    authentication_classes = (KeySecretAuthentication,)

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
            client=AppClient.objects.first()
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
                    client=AppClient.objects.first(),
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
        user = User.objects.filter(username=request.GET.get('username')).first()
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

        If UserNotFound - return status 404 w/ msg User not found.
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
            rules = badge.get("rules", {}).get("actions", {})
            default_progress = {k: {'count': 0, 'goal': v} for k, v in rules.items()}
            user_stats = badge.get("users", {}).get(str(user.id), {})

            # Exclude inactive rules (actions rules might have changed)
            for a in set(user_stats.keys()).difference(set(rules.keys())).intersection(set(user_stats)):
                del user_stats[a]

            default_progress.update(user_stats)
            c_badges().update(
                {"user_id": user.id},
                {
                    "$set": {
                        "badges.{}.progress".format(badge.get("slug")): default_progress
                    }
                },
                upsert=True
            )

            # Check if a badge is already granted
            # NOTE: consider adding 'done_date` (we'll be able to define if rules were
            # changed after a badge was granted)
            if not c_badges().find_one(
                {"user_id": user.id}
            ).get(
                "badges", {}
            ).get(
                badge.get("slug"), {}
            ).get(
                "done"
            ):
                done = all(
                    map(
                        lambda x: x[0] >= x[1] if x[1] else False,
                        (
                            (user_stats[i].get('count', 0), rules.get(i))
                            for i in user_stats if not i == 'done')
                    )
                ) if user_stats else False
                sql_achievement = Achievement.objects.filter(slug=badge.get("slug")).first()
                achievement_url = sql_achievement.badge_img.url if sql_achievement else ''
                c_badges().update(
                    {"user_id": user.id},
                    {
                        "$set": {
                            "badges.{}.done".format(badge.get("slug")): done,
                            "badges.{}.url".format(badge.get("slug")): achievement_url
                        }
                    },
                )

        log_api_access = ApiAccessEvent(
            user=user,
            api_name='Badges'
        )
        log_api_access.save()
        res = c_badges().find_one({"user_id": user.id}, {"_id": 0})

        if res:
            res_budges = OrderedDict(sorted(res.get('badges').items(), key=lambda x: x[1]['done'], reverse=True))
            return Response(res_budges if res else {})

        return Response({}, status=status.HTTP_404_NOT_FOUND)


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
        user_statuses = StatusBadge.objects.all()
        game_profile = GameProfile.objects.get(user=user)

        serializer = StatusSerializer(
            user_statuses, context={'request': request, 'progress': game_profile.points}, many=True
        )

        serializer_data = sorted(serializer.data, key=lambda i: i['done'])
        return Response(serializer_data)


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
        return Response(badge.get('rules', {}) if badge else {})

    def put(self, request, *args, **kwargs):
        slug = request.data.pop('slug')
        if slug:
            self.conn.collection.update({'slug': slug}, {"$set": {'rules': request.data, 'active': True}}, upsert=True)
            return Response({}, status=200)
        return Response({'message': 'Something went wrong'}, status=400)


class CoursesView(APIView):
    """
    Courses list from edx-platform.
    """

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        client = EdxApiV2Client()
        try:
            return Response(
                {'courses': client.get_courses()},
                status=http.client.OK
            )
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
        ) as e:
            return Response(
                {'courses': []},
                status=e.status_code
            )


class OrganizationsView(APIView):
    """
    Existing organisations from edx-platform.
    """

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        client = EdxApiV2Client()
        try:
            return Response(
                {'organisations': client.get_organizations()},
                status=http.client.OK
            )
        except (
            EdxApiNotFoundException,
            EdxApiResponseParsingException,
            EdxApiServerErrorException,
            EdxApiUnauthorizedException,
            OtherEdxApiException,
        ) as e:
            return Response(
                {'organisations': []},
                status=e.status_code
            )


class AchievementsView(APIView):

    def post(self, request):
        errors = ''
        slug = request.POST.get('slug')
        try:
            achievement = Achievement.objects.get(slug=slug)
            form = AchievementForm(request.POST, request.FILES, instance=achievement)
            if form.is_valid():
                form.save()
                return Response({}, status=200)
            else:
                errors = form.errors
        except Achievement.DoesNotExist as e:
            errors = 'Entry with "slug" - {} does not exist'.format()
        return Response({'errors': errors}, status=400)

    def delete(self, request):
        slug = request.data.get('slug')
        Achievement.objects.get(slug=slug).delete()
        return Response({}, status=200)


class LeaderBoardView(APIView):

    def get(self, request):
        top = [
            _id
            for i in GameProfile.objects.order_by('-points')[:100].values_list('id')
            for _id in i
        ]
        try:
            rank = top.index(request.user.gameprofile.id) + 1
        except (ValueError, AttributeError):
            rank = None
        gameprofiles = GameProfile.objects.order_by('-points')
        return Response({
            'gameprofiles': GameProfileSerializer(gameprofiles, many=True).data,
            'rank': rank
        }, status=200, content_type='application/json')

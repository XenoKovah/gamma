import logging
from collections import OrderedDict
from datetime import datetime, timedelta

import http.client

from django.contrib.auth.models import User
from django.db.models import F
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

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
    LoggedEventSerializer,
    ApiAccessEventSerializer,
    UserStatusSerializer,
    StatusSerializer,
    EventSerializer,
    StatusBadgeSlugSerializer
)

from core.services import MongoConnector
from core.authentication import KeySecretAuthentication
from core.models import GameProfile, AppClient
from core.mongo import c_badges
from achievements.services import AchievementRulesMongo
from pointlog.models import LoggedEvent
from pointlog.models import ApiAccessEvent
from pointlog.tasks import update_user_position, update_users_badge_data
from achievements.models import Achievement, StatusBadge, Event
from achievements.forms import AchievementForm


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
USER_NOT_FOUND = 'User not found'
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
        course_id = self.request.data.get('course_id', '')
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

                game_profile = GameProfile.objects.get(user=user)
                serializer = GameProfileSerializer(game_profile, context={'request': request})

                # Logging this event to prevent repeating
                log_event = LoggedEvent(
                    uniq_id=uniq_id,
                    user=user,
                    event_type=event_type,
                    org=org,
                    course_id=course_id,
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

                logged_event_data = LoggedEventSerializer(log_event).data
                logged_event_data.update({
                    'award': event.award
                })

                update_user_position.delay(
                    user.id,
                    user.username,
                    game_profile.points,
                    logged_event_data
                )
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
                {"Error": USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )
        game_profile = GameProfile.objects.get(user=user)
        serializer = GameProfileSerializer(game_profile, context={'request': request})

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
                {"Error": USER_NOT_FOUND},
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
                {"Error": USER_NOT_FOUND},
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
        serializer = GameProfileSerializer(game_profile, context={'request': request})

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
        conn = AchievementRulesMongo()
        conn.connect()
        badges_rules = conn.collection.find({"active": True})

        user = User.objects.filter(
            username=request.GET.get('username')
        ).first()
        user_badges = {}
        if user:
            log_api_access = ApiAccessEvent(
                user=user,
                api_name='Badges'
            )
            log_api_access.save()
            user_badges = c_badges().find_one({"user_id": user.id}, {"_id": 0}) or {}
            user_badges = user_badges.get('badges', {})

        result = {}
        for badge in badges_rules:
            badge_granted = user_badges.get(badge['slug'], {}).get('done', False)
            user_progress = user_badges.get(badge['slug'], {}).get('progress', {})
            rules = badge.get('rules', {}).get('actions', {})
            if badge_granted:
                progress = user_progress
            else:
                progress = {
                    event: {
                        'count': user_progress.get(event, {}).get('count', 0),
                        'goal': rules[event],
                    } for event in rules.keys()
                }
            result[badge['slug']] = {
                'done': badge_granted,
                'url': badge.get('url'),
                'progress': progress
            }

        result = OrderedDict(sorted(result.items(), key=lambda x: x[1]['done'], reverse=True))
        return Response(result)


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
                {"Error": USER_NOT_FOUND},
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
                {"Error": USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )
        qs = LoggedEvent.objects.filter(
            user=user, date__gte=datetime.now() - timedelta(minutes=5)
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


class ActionsListView(APIView):
    """
    Return all available actions for badges granting rules.

    Contains all Events that are set in system,
    and additional items 'badge' and 'status_badge'
    for 'badge-for-badge' granting.
    """
    def get(self, request, *args, **kwargs):
        """
        Get all Actions.
        """
        qs = Event.objects.all()
        serializer = EventSerializer(qs, many=True)
        data = [
            {"event_type": "badge"},
            {"event_type": "status_badge"},
        ]
        data.extend(serializer.data)
        return Response(data)


class BadgesListView(APIView):
    """
    Get available badges (for those rules are set).
    """

    def get(self, request, *args, **kwargs):
        conn = AchievementRulesMongo()
        conn.connect()
        badges = conn.collection.find({"active": True})
        data = [badge['slug'] for badge in badges if 'slug' in badge]
        return Response(data)


class StatusBadgesListView(generics.ListAPIView):
    """
    Get all status badges
    """
    queryset = StatusBadge.objects.all()
    serializer_class = StatusBadgeSlugSerializer


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
        achievement = Achievement.objects.filter(slug=slug).first()
        if slug and achievement:
            old_rules = (self.conn.collection.find_one({'slug': slug}) or {}).get('rules')
            new_rules = request.data
            badge_url = request.build_absolute_uri(achievement.badge_img.url)
            self.conn.collection.update(
                {'slug': slug},
                {"$set":
                    {
                        'rules': new_rules, 'active': True,
                        'url': badge_url
                    }},
                upsert=True
            )
            if old_rules and new_rules:
                # don't try to open the badge for users if it's rules are completely deleted
                update_users_badge_data(slug, old_rules, new_rules, badge_url)
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
                conn = AchievementRulesMongo()
                conn.connect()
                badge_url = request.build_absolute_uri(achievement.badge_img.url)
                conn.collection.update(
                    {'slug': slug},
                    {"$set": {'url': badge_url}},
                )
                return Response({}, status=200)
            else:
                errors = form.errors
        except Achievement.DoesNotExist as e:
            errors = f'Entry with {slug=} does not exist'
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
            'gameprofiles': GameProfileSerializer(gameprofiles, context={'request': request}, many=True).data,
            'rank': rank
        }, status=200, content_type='application/json')

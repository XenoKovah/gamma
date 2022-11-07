import logging

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from edx_integration.api.v2.client import EdxApiV2Client
from edx_integration.api.v2.exceptions import (
    EdxApiNotFoundException,
    EdxApiResponseParsingException,
    EdxApiServerErrorException,
    EdxApiUnauthorizedException,
    OtherEdxApiException,
)

from core import db
from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils, clean_rules
from core.data_models.models import EventModel, Rules
from core.tasks import update_user_position, update_users_badge_data

from achievements.models import Achievement
from achievements.forms import AchievementForm


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
USER_NOT_FOUND = 'User not found'
logger = logging.getLogger('events')


class GameProfileView(APIView, AppClientUtils):
    """
    GET or UPDATE user points.
    """
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
        event_data = EventModel(request.data, strict=False)

        if not (system_event := db.events.read_one(event_data.event_type)):
            return Response(
                {"Error": "Event type is not recognizable"},
                status=status.HTTP_406_NOT_ACCEPTABLE)
        event_data.points = system_event.award
        event_data.title = system_event.title

        app_client = self.get_app_client(request)
        event_data.client = app_client.uid

        if not (event := db.events.log(event_data)):
            resp_msg = 'Repeated event occurs'
            logger.debug(f'For user {event_data.username} msg: {resp_msg}: {event_data.event_type}::{event_data.uid}')
            return Response({"Error": resp_msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

        points = db.users.update_profile(event.username, event)

        logger.debug('For user {0} msg: {1}'.format(
            event.username,
            f'Event logged::{event.uid=}::{event.event_type=}::{event.points=}'))

        update_user_position.delay(event.username, points, event.to_primitive())

        return Response(event.to_primitive('public'), status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        user = db.users.read_one(user_uid)
        user.system_statuses = db.statuses.read()
        user.system_badges = db.badges.read_active()
        user.system_events = db.events.read()

        return Response(user.to_primitive('public'))


class ActionsListView(APIView):
    """
    Return all available actions for badges granting rules.

    Contains all Events that are set in system,
    and additional items 'badge' and 'status_badge'
    for 'badge-for-badge' granting.
    """
    def get(self, *args, **kwargs):
        """
        Get all Actions.
        """
        events = [event.to_primitive('public') for event in db.events.read()]
        data = [
            {"event_type": "badge"},
            {"event_type": "status_badge"},
        ]
        data.extend(events)
        return Response(data)


class BadgesView(APIView):
    """
    Get available badges (for those rules are set).
    """

    def get(self, *args, **kwargs):
        badges = db.badges.read_active()
        data = [badge.badge_uid for badge in badges if badge]

        return Response(data)


class StatusBadgesView(APIView):
    """
    Get all status badges
    """

    def get(self, *args, **kwargs):
        statuses = [status.to_primitive('public') for status in db.statuses.read()]
        return Response(statuses)


class FiltersView(APIView):
    """
    Return all available Filters.
    """
    @staticmethod
    def get(*args, **kwargs):
        """
        Get all Filters.
        """
        return Response([
            {'org': 'String'},
            {'interval': {'start': 'Date', 'end': 'Date'}},
            {'frequency': 'Int32'}])


class BadgeRulesView(APIView):
    permission_classes = [IsAdminUser]
    """
    Return Badge rules.
    """
    def get(self, request, *args, **kwargs):
        """
        Get rules for badge by a slug.
        """
        slug = request.GET.get('slug')
        if not slug:
            return Response({})
        badge = db.badges.read_one(badge_uid=slug)
        return Response(badge.to_primitive('public').get('rules', {}) if badge else {})

    def put(self, request, *args, **kwargs):
        slug = request.data.pop('slug')

        if not (badge_model := Achievement.objects.filter(slug=slug).first()):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        with db.badges.read_and_update(slug) as badge:
            if badge:
                old_rules = badge.rules
                new_rules = Rules(clean_rules(request.data), validate=True)

                badge.update_badge({"rules": request.data})

        if not badge:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        if old_rules and new_rules:
            # don't try to open the badge for users if it's ruldataes are completely deleted
            update_users_badge_data.delay(slug, old_rules.to_primitive(), new_rules.to_primitive(),
                                          badge_model.badge_img.url, badge_model.title, badge_model.description)

        return Response({}, status=status.HTTP_200_OK)


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
                status=status.HTTP_200_OK
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
                status=status.HTTP_200_OK
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

                return Response({}, status=status.HTTP_200_OK)

            else:
                errors = form.errors

        except Achievement.DoesNotExist:
            errors = f'Entry with {slug} does not exist'

        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        slug = request.data.get('slug')
        Achievement.objects.get(slug=slug).delete()
        return Response({}, status=status.HTTP_200_OK)


class LeaderBoardView(APIView):
    """
    Return leaderbord data.
    """
    def get(self, request):
        user_uid = request.GET.get('username')
        if user_uid and not (user := db.users.read_one(user_uid)):
            return Response(
                {"Error": USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND)

        leaders = db.leaders.read()
        system_statuses = db.statuses.read()

        try:
            rank = leaders.roster.index(user) + 1 if user_uid else None
        except ValueError:
            rank = None
        return Response({
            'gameprofiles': leaders.to_primitive('roster').get("roster"),
            'rank': rank,
            'system_statuses': [status.to_primitive('public') for status in system_statuses]

        }, status=status.HTTP_200_OK, content_type='application/json')


class BadgeDependentBadgesView(APIView):

    def get(self, request):
        if slug := request.GET.get('slug'):
            return Response(db.badges.dependent_badges(slug),
                            status=status.HTTP_200_OK,
                            content_type='application/json')

        return Response(status=status.HTTP_400_BAD_REQUEST)


class StatusDependentBadgesView(APIView):

    def get(self, request):
        if slug := request.GET.get('slug'):
            return Response(db.statuses.dependent_badges(slug),
                            status=status.HTTP_200_OK,
                            content_type='application/json')

        return Response(status=status.HTTP_400_BAD_REQUEST)

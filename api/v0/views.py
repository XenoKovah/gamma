import json
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
from core.db.engine import conn
from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils, clean_rules
from core.data_models.models import Rules
from core.tasks import update_user_position, update_users_badge_data

from events.exceptions import (
    EventDataIsNotCorrectError,
    EventTypeIsNotRecognizableError,
    DuplicatedEventOccursError,
)
from events.usecases import ProcessIncomingEventUseCase, GetEventsUseCase
from events.repository import EventRepository
from schematics.exceptions import DataError

# from achievements.models import Achievement
# from achievements.forms import AchievementForm


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
        data = self.update_data_with_client_uid()

        try:
            repository = EventRepository(conn.db)
            event = ProcessIncomingEventUseCase(repository).execute(data)
        except (
            EventDataIsNotCorrectError,
            EventTypeIsNotRecognizableError,
            DuplicatedEventOccursError,
            DataError) as err:
            return Response({"Error": str(err)}, status=status.HTTP_406_NOT_ACCEPTABLE)


        points = db.users.update_profile(event.username, event)

        logger.debug('For user {0} msg: {1}'.format(  # pylint: disable=logging-format-interpolation
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

        repository = EventRepository(conn.db)
        user.system_events = GetEventsUseCase(repository).execute()

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
        repository = EventRepository(conn.db)
        events = GetEventsUseCase(repository).execute(public=True)

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
    Get all status badges.
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
    """
    Return Badge rules.
    """

    permission_classes = [IsAdminUser]

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
            update_users_badge_data.delay(slug, old_rules.to_primitive(), new_rules.to_primitive(),  # pylint: disable=no-value-for-parameter
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

            if form.is_valid():  # pylint: disable=no-else-return
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

        if (user_signup_source := request.GET.get('signup_source')):  # pylint: disable=superfluous-parens
            if user_signup_source == settings.MAIN_SIGNUP_SOURCE:
                leaders = db.leaders.read_with_main_signup_source()
            else:
                leaders = db.leaders.read_with_signup_source(user_signup_source)
        else:
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
    """
    Status badges dependencies API view.
    """

    def get(self, request):
        """
        Get the status badge dependencies.

        Requires a 'status_badges_slugs' list containing status badges' slugs in the request data.

        Returns:
            dict: badge slug as a key and the list of its dependencies titles as a values.
            Example response:
                {
                    'slug_status_badge_1': ['dependency_1', 'dependency_2'],
                    'slug_status_badge_2': ['dependency_3'],
                    ....
                    'slug_status_badge_n': ['dependency_x', ...],
                }

        Returns:
            400 - if there is empty list 'status_badges_deps' in the request data.
        """
        if slugs := request.GET.getlist('status_badges_slugs'):
            status_badges_deps = {}
            for slug in slugs:
                if dependency := db.statuses.dependent_badges(slug):
                    status_badges_deps[slug] = dependency
            return Response(
                status_badges_deps,
                status=status.HTTP_200_OK,
                content_type='application/json'
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SignupSourceUpdateView(APIView):
    """
    API endpoint to update game profiles with signup source data.
    """

    def post(self, request):
        """
        Update game profiles with signup source data.

        Args:
            Request data should be in JSON format.

        Returns:
            Response with status 200 if update was successful,
            Response with status 500 if an error occurred.
        """
        try:
            count_users = 0
            if users_data := json.loads(request.data):
                if (user_uids := users_data.get('uids')) and (signup_source := users_data.get('tenant')):
                    result = conn.db.users.update_many(
                        filter={
                            'user_uid': {'$in': user_uids}},
                        update={
                            '$set': {'signup_source': signup_source}}
                    )
                    count_users = result.modified_count

            return Response({'count': count_users}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'count': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

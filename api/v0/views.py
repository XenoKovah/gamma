import logging

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
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

from core import db
from core.authentication import KeySecretAuthentication
from core.utils import AppClientUtils, merge_statuses
from core.data_models.models import EventModel
from core.utils import compile_user_badges
from core.tasks import update_user_position, update_users_badge_data

from achievements.models import Achievement, Event
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
        event_data = EventModel().import_data(request.data)

        if not (system_event := db.read_system_event(event_data.event_type)):
            return Response(
                {"Error": "Event type is not recognizable"},
                status=status.HTTP_406_NOT_ACCEPTABLE)
        event_data.points = system_event.award

        app_client = self.get_app_client(request)
        event_data.client = app_client.uid

        if not (event := db.log_event(event_data)):
            resp_msg = 'Repeated event occurs'
            logger.debug(f'For user {event_data.username} msg: {resp_msg}: {event_data.event_type}::{event_data.uid}')
            return Response({"Error": resp_msg}, status=status.HTTP_406_NOT_ACCEPTABLE)

        points = db.update_game_profile(event_data.username, event.points)

        logger.debug('For user {0} msg: {1}'.format(
            event_data.username,
            f'Event logged::{event.uid=}::{event.event_type=}::{event.points=}'))

        update_user_position(event_data.username, points, event.to_primitive())

        return Response(event.to_primitive(), status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        user = db.read_user(user_uid)

        badges_rules = db.read_active_badges()
        user_badges = db.read_user_badges(request.GET.get('username'))

        badges = compile_user_badges(badges_rules, user_badges)
        user.statuses = merge_statuses(db.read_statuses(), user)
        response = user.to_primitive('public')

        response['badges'] = badges

        return Response(response)


class ProgressView(APIView):
    """
    Retrieve User progress.
    """
    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user GameProfile data.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        data = [_.to_primitive('public') for _ in db.read_progress(user_uid)]

        return Response(data)


class ChartView(APIView):
    """
    Retrieve User chart.
    """
    def get(self, request, *args, **kwargs):
        """
        Simply retrieve user chart data.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        
        data = {}

        if (progress_data := db.read_charted_progress(user_uid)):
            # TODO: get rid of this
            for key in progress_data:
                event_title, order = Event.objects.values_list(
                    'title', 'color'
                ).filter(event_type=key).first()
                if event_title:
                    data[event_title] = (order, progress_data[key])
                else:
                    data[key] = (order, progress_data[key])

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
        if not (user_uid := request.GET.get('username')):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        user = db.read_user(user_uid)

        return Response({"points": user.points})


class BadgesView(APIView):
    """
    Badges API.
    """
    def get(self, request, *args, **kwargs):
        """
        Get badges for particular user_uid.

        If UserNotFound - return status 404 w/ msg User not found.
        """
        badges_rules = db.read_active_badges()
        # TODO: use UserBadges model to serialize
        user_badges = db.read_user_badges(request.GET.get('username'))

        return Response(compile_user_badges(badges_rules, user_badges))


class UserStatuses(APIView):
    """
    Return achieved statuses.
    """
    def get(self, request, *args, **kwargs):
        """
        Get user's statuses.
        """
        # TODO: use aggregation addField
        user = db.read_user(request.GET.get('username'))
        statuses = db.read_statuses()

        merged_statuses = merge_statuses(statuses, user)

        if not user:
            return Response(
                {"Error": USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND)

        return Response([_.to_primitive('public') for _ in merged_statuses if _])


class StatusView(APIView):
    """
    Statuses API.
    """
    def get(self, request, *args, **kwargs):
        """
        Get configured statuses.
        """
        statuses = db.read_statuses()

        return Response([status.to_primitive('public') for status in statuses])


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
        events = [event.to_primitive() for event in db.read_events()]
        data = [
            {"event_type": "badge"},
            {"event_type": "status_badge"},
        ]
        data.extend(events)
        return Response(data)


class BadgesListView(APIView):
    """
    Get available badges (for those rules are set).
    """

    def get(self, *args, **kwargs):
        badges = db.read_active_badges()
        data = [badge['slug'] for badge in badges if 'slug' in badge]
        return Response(data)


class StatusBadgesListView(APIView):
    """
    Get all status badges
    """

    def get(self, *args, **kwargs):
        statuses = [status.to_primitive() for status in db.read_statuses()]
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
    def get(self, request, *args, **kwargs):
        """
        Get rules for badge by a slug.
        """
        slug = request.GET.get('slug')
        if not slug:
            return Response({})
        badge = db.read_badge(badge_uid=slug)
        return Response(badge.get('rules', {}) if badge else {})

    def put(self, request, *args, **kwargs):
        slug = request.data.pop('slug')

        if not (badge_model := Achievement.objects.filter(slug=slug).first()):
            return Response({"Error": "user_uid must be set"}, status=status.HTTP_400_BAD_REQUEST)

        badge_url = request.build_absolute_uri(badge_model.badge_img.url)
        data = request.data
        data.update({'url': badge_url})

        with db.read_badge_and_update(slug) as badge:
            if badge:
                old_rules = badge.rules.to_native() if badge.rules else None
                new_rules = request.data
            active = True if new_rules else False
            badge.update_badge({"rules": request.data, "active": active})

        db.activate_badge(slug)

        if old_rules and new_rules:
            # don't try to open the badge for users if it's ruldataes are completely deleted
            update_users_badge_data.delay(slug, old_rules, new_rules, badge_url)

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

                data = {"title": form.cleaned_data.get("title"),
                        "url": request.build_absolute_uri(achievement.badge_img.url)}

                with db.read_badge_and_update(slug) as badge:
                    badge.update_badge(data)

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
        if user_uid and not (user := db.read_user(user_uid)):
            return Response(
                {"Error": USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND)

        leaders = db.read_leaders()

        try:
            rank = leaders.roster.index(user) + 1 if user_uid else None
        except ValueError:
            rank = None
        return Response({
            'gameprofiles': leaders.to_primitive('roster').get("roster"),
            'rank': rank
        }, status=status.HTTP_200_OK, content_type='application/json')

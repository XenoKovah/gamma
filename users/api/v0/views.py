from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from achievements.serializers import BadgeNotificationSerializer
from achievements.usecases import MarkBadgeNotificationsSeenUseCase, PendingBadgeNotificationsUseCase
from core.authentication import KeySecretAuthentication
from leaderboard.repository import RedisLeaderboardRepository, RedisLeaderboardsPendingUpdateRepository
from leaderboard.usecases import EnqueueLeaderboardsUpdateUseCase, RemoveUserFromLeaderboardsUseCase
from users.api.v0.serializers import BadgeNotificationsSeenSerializer, UserGameProfileSerializer
from users.models import GammaUser
from users.serializers import GammaUsersSignupSourceSerializer
from users.usecases import SignupSourceUpdateUseCase


class UserGameProfileView(APIView):
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

        gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid)
        serializer = UserGameProfileSerializer(instance=gamma_user, context={'user_uid': user_uid})

        return Response(serializer.data)


class BadgeNotificationsView(APIView):
    """
    Pending "badge earned" notifications API view.

    Lists badge achievements the user completed but has not yet been shown a
    notification for. Deliberately does NOT create a GammaUser for unknown
    usernames — polling must stay read-only.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        """
        Get the user's pending badge notifications, oldest first.
        """
        if not (user_uid := request.GET.get('username')):
            return Response({'Error': 'username must be set'}, status=status.HTTP_400_BAD_REQUEST)

        pending = PendingBadgeNotificationsUseCase().execute(user_uid)
        serializer = BadgeNotificationSerializer(pending, many=True)

        return Response(serializer.data)


class BadgeNotificationsSeenView(APIView):
    """
    Acknowledge shown badge notifications API view.
    """

    authentication_classes = (KeySecretAuthentication,)

    def post(self, request: Request) -> Response:
        """
        Mark the given achievements' notifications as seen for the user.
        """
        serializer = BadgeNotificationsSeenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        count = MarkBadgeNotificationsSeenUseCase().execute(
            serializer.validated_data['username'],
            serializer.validated_data['uuids'],
        )

        return Response({'count': count}, status=status.HTTP_200_OK)


class SignupSourceUpdateView(APIView):
    """
    Gamma users signup source bulk update API view.
    """

    def post(self, request: Request) -> Response:
        serializer = GammaUsersSignupSourceSerializer(data=request.data)
        serializer.is_valid()

        updated_user_count = SignupSourceUpdateUseCase().execute(serializer.validated_data)

        return Response({'count': updated_user_count}, status=status.HTTP_200_OK)


class LeaderboardOptOutView(APIView):
    """
    Read or set a user's "exclude me from leaderboards" flag.

    GET ?username=<uid> -> {"excluded": bool}: the user's current opt-out state.
    POST {"username": <uid>, "excluded": bool}: set it. Opting out evicts the user
    from every Redis leaderboard immediately; opting back in re-enqueues them so the
    next update cycle restores their scores. The dashboard (running in the LMS) calls
    this on behalf of the signed-in learner from the Account Settings toggle.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        if not (user_uid := request.GET.get('username')):
            return Response({'Error': 'username must be set'}, status=status.HTTP_400_BAD_REQUEST)

        gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid)
        return Response({'excluded': gamma_user.excluded_from_leaderboard})

    def post(self, request: Request) -> Response:
        user_uid = request.data.get('username')
        excluded = request.data.get('excluded')

        if not user_uid or not isinstance(excluded, bool):
            return Response(
                {'Error': 'username (str) and excluded (bool) are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid)
        was_excluded = gamma_user.excluded_from_leaderboard

        if excluded != was_excluded:
            gamma_user.excluded_from_leaderboard = excluded
            gamma_user.save(update_fields=('excluded_from_leaderboard',))

            if excluded:
                # Evict immediately so they disappear from leaderboards right away; the
                # build/update pipeline will not re-add them while the flag is set.
                course_ids = list(gamma_user.courses_points.values_list('course_id', flat=True))
                RemoveUserFromLeaderboardsUseCase(RedisLeaderboardRepository()).execute(
                    user_uid, gamma_user.signup_source, course_ids
                )
            else:
                # Opted back in: schedule an update so their scores are restored.
                EnqueueLeaderboardsUpdateUseCase(
                    RedisLeaderboardsPendingUpdateRepository()
                ).execute(user_uid)

        return Response({'excluded': excluded}, status=status.HTTP_200_OK)


class ExcludedUserUidsView(APIView):
    """
    List the user_uids of everyone who opted out of leaderboard ranking.

    The dashboard uses this to drop opted-out learners from the one leaderboard section
    it ranks itself (the per-course "In progress" list, ranked by grade %); the
    point-ranked sections are filtered by Gamma directly.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        excluded_uids = list(
            GammaUser.objects.filter(excluded_from_leaderboard=True).values_list('user_uid', flat=True)
        )
        return Response({'user_uids': excluded_uids})

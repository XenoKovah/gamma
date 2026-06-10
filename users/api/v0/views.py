from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from achievements.serializers import BadgeNotificationSerializer
from achievements.usecases import MarkBadgeNotificationsSeenUseCase, PendingBadgeNotificationsUseCase
from core.authentication import KeySecretAuthentication
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

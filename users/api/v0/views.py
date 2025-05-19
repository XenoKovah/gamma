from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from core.authentication import KeySecretAuthentication
from users.api.v0.serializers import UserGameProfileSerializer
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


class SignupSourceUpdateView(APIView):
    """
    Gamma users signup source bulk update API view.
    """

    def post(self, request: Request) -> Response:
        serializer = GammaUsersSignupSourceSerializer(data=request.data)
        serializer.is_valid()

        updated_user_count = SignupSourceUpdateUseCase().execute(serializer.validated_data)

        return Response({'count': updated_user_count}, status=status.HTTP_200_OK)

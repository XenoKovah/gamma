from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from avatars.api.v0.serializers import AvatarSetSerializer, AvatarSerializer, UserAvatarConfigSerializer
from avatars.constants import AVATAR_SET_FINISH_FAILURE, AVATAR_SET_FINISH_SUCCESS
from avatars.models import Avatar, AvatarSet, UserAvatarConfig
from core.authentication import KeySecretAuthentication
from core.mixins import AdminUserPermissionMixin


class AvatarSetViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing Avatar Set.
    """

    queryset = AvatarSet.objects.all()
    serializer_class = AvatarSetSerializer

    @action(detail=True, methods=['patch'], url_path='finish')
    def finish_avatar_set(self, request, pk=None):
        """
        Custom action to update 'is_draft' to False.
        """
        avatar_set = self.get_object()

        if avatar_set.avatars.count() < 2:
            return Response(
                {'error': AVATAR_SET_FINISH_FAILURE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        avatar_set.is_draft = False
        avatar_set.save()

        return Response(
            {'message': AVATAR_SET_FINISH_SUCCESS},
            status=status.HTTP_200_OK,
        )


class AvatarViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing single Avatar.
    """

    queryset = Avatar.objects.all().prefetch_related('rules')
    serializer_class = AvatarSerializer


class UserAvatarConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User Avatar Configurations.
    """
    queryset = UserAvatarConfig.objects.all()
    serializer_class = UserAvatarConfigSerializer

    # TODO: find way to check Authentication state for request from edX.
    # authentication_classes = (KeySecretAuthentication,)

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from achievements.services.progress import AvatarProgressService
from avatars.api.v0.serializers import (
    AvatarProgressSerializer,
    AvatarSerializer,
    AvatarSetSerializer,
    UserAvatarConfigSerializer,
)
from avatars.constants import AVATAR_SET_FINISH_FAILURE, AVATAR_SET_FINISH_SUCCESS
from avatars.models import Avatar, AvatarSet, UserAvatarConfig
from core.authentication import KeySecretAuthentication
from core.mixins import AdminUserPermissionMixin

AVATARS_API_TAG = 'Avatars'


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
    queryset = (
        UserAvatarConfig.objects.select_related('user', 'avatar_set')
        .prefetch_related('avatar_set__avatars__rules')
        .all()
    )
    serializer_class = UserAvatarConfigSerializer
    authentication_classes = (KeySecretAuthentication,)

    @swagger_auto_schema(
        method='get',
        operation_summary='Get avatar progress for a configuration.',
        operation_description=(
            'Calculate progress data for the avatar associated with the specified UserAvatarConfig.'
        ),
        responses={
            200: AvatarProgressSerializer,
        },
        tags=[AVATARS_API_TAG],
    )
    @action(detail=True, methods=['get'], url_path='progress')
    def get_progress(self, request, pk=None):
        config = self.get_object()
        service = AvatarProgressService(config)
        progress = service.calculate_progress()
        serializer = AvatarProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)

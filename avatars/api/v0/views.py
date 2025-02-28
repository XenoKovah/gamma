from rest_framework import viewsets

from avatars.api.v0.serializers import AvatarSetSerializer, AvatarSerializer
from avatars.models import (
    Avatar,
    AvatarSet,
    UserAvatarConfig,
)
from core.mixins import AdminUserPermissionMixin


class AvatarSetViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing Avatar Set.
    """

    queryset = AvatarSet.objects.all()
    serializer_class = AvatarSetSerializer


class AvatarViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing single Avatar.
    """

    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer

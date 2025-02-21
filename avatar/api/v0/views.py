from rest_framework import viewsets

from avatar.api.v0.serializers import AvatarSetSerializer, AvatarSerializer
from avatar.models import (
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

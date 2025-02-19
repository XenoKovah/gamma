from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from avatar.api.v0.serializers import AvatarSetSerializer, AvatarSerializer
from avatar.models import (
    Avatar,
    AvatarSet,
    UserAvatarConfig,
)


class AvatarSetViewSet(viewsets.ModelViewSet):
    """
    View set provides CRUD operations for managing Avatar Set.
    """

    queryset = AvatarSet.objects.all()
    serializer_class = AvatarSetSerializer

    def get_permissions(self):
        """
        Check user permission.
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

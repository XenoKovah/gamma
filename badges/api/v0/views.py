from rest_framework import viewsets

from badges.models import Badge
from core.mixins import AdminUserPermissionMixin

from .serializers import BadgeSerializer


class BadgeViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer

from rest_framework import viewsets

from badges.models import Badge
from core.mixins import AdminUserPermissionMixin

from .serializers import BadgeSerializer


class BadgeViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.all().prefetch_related('rules')
    serializer_class = BadgeSerializer

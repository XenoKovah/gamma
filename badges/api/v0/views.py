from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from badges.models import Badge

from .serializers import BadgeSerializer


class BadgeViewSet(viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.filter(is_active=True)
    serializer_class = BadgeSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

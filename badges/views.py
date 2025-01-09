from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from badges.models import Badge
from badges.serializers import BadgeSerializer


class BadgeViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = Badge.objects.filter(active=True)
    serializer_class = BadgeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

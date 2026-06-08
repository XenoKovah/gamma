from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from achievements.reconciliation import recompute_holders
from badges.models import Badge
from core.mixins import AdminUserPermissionMixin

from .serializers import BadgeSerializer


class BadgeViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.all().prefetch_related('rules')
    serializer_class = BadgeSerializer

    @action(detail=True, methods=['post'])
    def recompute(self, request, pk=None):
        """
        Manually re-evaluate, under the badge's current rules, which users should hold it.

        Grants the badge to users whose stored event history now satisfies every rule
        (e.g. people who completed the courses before the badge or rule was added) and
        revokes it from users who no longer qualify after a rules change.
        """
        badge = self.get_object()
        result = recompute_holders(badge)
        return Response({
            'badge_id': badge.id,
            'granted': result.granted,
            'revoked': result.revoked,
            'unchanged': result.unchanged,
        })

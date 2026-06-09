from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from achievements.reconciliation import recompute_holders
from badges.models import Badge
from core.mixins import AdminUserPermissionMixin
from users.models import GammaUser

from .serializers import BadgeAssignmentSerializer, BadgeSerializer


class BadgeViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.all().prefetch_related('rules')
    serializer_class = BadgeSerializer

    # State-changing custom actions that must be admin-only. ``AdminUserPermissionMixin``
    # only guards the default write actions (create/update/partial_update/destroy), so
    # without listing them here these actions would inherit the empty (public) permission set.
    ADMIN_ONLY_ACTIONS = ('assign', 'unassign', 'recompute')

    def get_permissions(self):
        """
        Restrict the custom admin-only actions to admins.
        """
        if self.action in self.ADMIN_ONLY_ACTIONS:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Manually grant this badge to one or more users by their user id.

        Body params:
            - user_uids (list[str]): GammaUser user_uids (edX usernames) to grant the badge to.

        Each listed user gets the badge (a rule-less, already-completed achievement) and,
        if the badge has ``points`` configured, those points are added to their total on the
        first grant. Re-assigning an already-granted badge is a no-op for that user (no double
        points), so the call is safe to retry.

        Returns HTTP 200 with ``{"granted": [...], "already_assigned": [...], "points_each": int}``.
        """
        badge = self.get_object()

        serializer = BadgeAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        granted, already_assigned = [], []
        for user_uid in serializer.validated_data['user_uids']:
            gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)
            if badge.award_to_user(gamma_user):
                granted.append(user_uid)
            else:
                already_assigned.append(user_uid)

        return Response(
            {
                'granted': granted,
                'already_assigned': already_assigned,
                'points_each': badge.points,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """
        Manually remove this badge from one or more users by their user id (inverse of ``assign``).

        Body params:
            - user_uids (list[str]): GammaUser user_uids (edX usernames) to remove the badge from.

        Each listed user loses the badge and, if it has ``points``, those points are deducted
        from their total (floored at 0). Removing a badge a user does not have is a no-op for
        that user, so the call is safe to retry.

        Returns HTTP 200 with ``{"removed": [...], "not_assigned": [...], "points_each": int}``.
        """
        badge = self.get_object()

        serializer = BadgeAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        removed, not_assigned = [], []
        for user_uid in serializer.validated_data['user_uids']:
            gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)
            if badge.revoke_from_user(gamma_user):
                removed.append(user_uid)
            else:
                not_assigned.append(user_uid)

        return Response(
            {
                'removed': removed,
                'not_assigned': not_assigned,
                'points_each': badge.points,
            },
            status=status.HTTP_200_OK,
        )

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

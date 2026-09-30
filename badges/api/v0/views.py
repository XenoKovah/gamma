from django.utils.timezone import now
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from achievements.reconciliation import recompute_holders
from badges.exceptions import BadgeExclusionError
from badges.models import Badge
from core.mixins import AdminUserPermissionMixin
from users.models import GammaUser

from .serializers import (
    BadgeAssignmentSerializer, BadgeAssignmentWithExpirySerializer, BadgeExpirySerializer, BadgeSerializer,
)


class BadgeViewSet(AdminUserPermissionMixin, viewsets.ModelViewSet):
    """
    Viewset provides CRUD operations for managing badges.
    """

    queryset = Badge.objects.all().prefetch_related('rules')
    serializer_class = BadgeSerializer

    # State-changing custom actions that must be admin-only. ``AdminUserPermissionMixin``
    # only guards the default write actions (create/update/partial_update/destroy), so
    # without listing them here these actions would inherit the empty (public) permission set.
    ADMIN_ONLY_ACTIONS = ('assign', 'unassign', 'recompute', 'holders', 'set_expiry', 'expire')

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

        Users disqualified by the badge's ``excluded_categories`` are reported in
        ``blocked`` rather than aborting the request, so one ineligible name in a bulk
        assign cannot strand the rest half-granted.

        Returns HTTP 200 with ``{"granted": [...], "already_assigned": [...],
        "blocked": [{"user_uid": str, "reason": str}], "points_each": int}``.
        """
        badge = self.get_object()

        serializer = BadgeAssignmentWithExpirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expires_at = serializer.validated_data.get('expires_at')
        if expires_at is not None and not badge.is_expiring:
            return Response({'detail': 'This badge is not an expiring badge.'}, status=status.HTTP_400_BAD_REQUEST)

        granted, already_assigned, blocked = [], [], []
        for user_uid in serializer.validated_data['user_uids']:
            gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)
            try:
                if badge.award_to_user(gamma_user, expires_at=expires_at):
                    granted.append(user_uid)
                else:
                    already_assigned.append(user_uid)
            except BadgeExclusionError as exc:
                blocked.append({'user_uid': user_uid, 'reason': str(exc)})

        return Response(
            {
                'granted': granted,
                'already_assigned': already_assigned,
                'blocked': blocked,
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

    def _expiring_badge_or_400(self):
        badge = self.get_object()
        if not badge.is_expiring:
            return badge, Response(
                {'detail': 'This badge is not an expiring badge.'}, status=status.HTTP_400_BAD_REQUEST,
            )
        return badge, None

    @action(detail=True, methods=['get'])
    def holders(self, request, pk=None):
        """
        List everyone holding this (expiring) badge with when each grant lapses.

        Returns ``{"holders": [{"user_uid", "awarded_at", "expires_at", "is_expired"}]}``, soonest
        expiry first and permanent grants last.
        """
        badge, error = self._expiring_badge_or_400()
        if error:
            return error
        return Response({
            'holders': [
                {
                    'user_uid': grant.user.user_uid,
                    'awarded_at': grant.completed_at,
                    'expires_at': grant.expires_at,
                    'is_expired': grant.is_expired,
                }
                for grant in badge.holders_with_expiry()
            ],
        })

    def _apply_expiry(self, request, forced_expires_at=None):
        badge, error = self._expiring_badge_or_400()
        if error:
            return error
        if forced_expires_at is None:
            serializer = BadgeExpirySerializer(data=request.data)
        else:
            serializer = BadgeAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expires_at = forced_expires_at if forced_expires_at is not None else serializer.validated_data['expires_at']

        updated, not_assigned = [], []
        for user_uid in serializer.validated_data['user_uids']:
            gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)
            (updated if badge.set_expiry(gamma_user, expires_at) else not_assigned).append(user_uid)

        return Response(
            {'updated': updated, 'not_assigned': not_assigned, 'expires_at': expires_at},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def set_expiry(self, request, pk=None):
        """
        Set (or clear) when the given users' existing grants of this badge lapse.

        Body params:
            - user_uids (list[str]): holders to re-date.
            - expires_at (datetime | null): new expiry; null makes the grants permanent, a past
              time expires them immediately. Points are not touched either way.

        Returns ``{"updated": [...], "not_assigned": [...], "expires_at": ...}``.
        """
        return self._apply_expiry(request)

    @action(detail=True, methods=['post'])
    def expire(self, request, pk=None):
        """
        Immediately expire the given users' grants of this badge (reversible via ``set_expiry``).

        Body params:
            - user_uids (list[str]): holders whose grant should lapse right now.
        """
        return self._apply_expiry(request, forced_expires_at=now())

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

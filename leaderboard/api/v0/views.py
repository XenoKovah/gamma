from typing import List, Optional

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievement
from badges.models import Badge
from badges.utils import is_achieved_badge
from core.authentication import KeySecretAuthentication
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.repository import ORMLeaderboardMemberDataRepository, RedisLeaderboardRepository
from leaderboard.usecases import GetPersonalizedLeaderboardUseCase
from users.models import GammaUser


class LeaderBoardView(APIView):
    """
    Provide personalized leaderboard data for the requesting Gamma user.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request):
        user_uid = request.GET.get("username")
        leaderboard_retrieving_context = LeaderboardRetrievingContext(
            user_uid,
            request.GET.get("signup_source"),
            request.GET.get("course_id"),
        )

        GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        response_data = self._collect_response_data(leaderboard_retrieving_context)

        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_response_data(self, leaderboard_retrieving_context: LeaderboardRetrievingContext) -> dict:
        """
        Collect data to place in the response body.
        """
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaders, competitors, rank = GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
        ).execute(leaderboard_retrieving_context)

        return {
            "top10": leaders,
            "rank": rank,
            "user_uid": leaderboard_retrieving_context.user_uid,
            "competitors": competitors,
        }


class BadgeLeaderBoardView(APIView):
    """
    Provide a leaderboard limited to the users who earned a specific badge.

    Unlike the personalized leaderboard, this returns a flat, points-ranked list
    of up to ``MEMBERS_LIMIT`` badge earners (not a window around the requesting
    user), together with the badge's display data. The response reuses the
    leaderboard member shape so the dashboard can render it with the regular
    leaderboard components.
    """

    authentication_classes = (KeySecretAuthentication,)

    MEMBERS_LIMIT = 100

    def get(self, request, badge_slug):
        user_uid = request.GET.get("username")
        signup_source = request.GET.get("signup_source")
        course_id = request.GET.get("course_id")

        badge = Badge.objects.filter(slug=badge_slug).order_by("-is_active", "pk").first()
        if badge is None:
            return Response({"error": "Badge not found."}, status=status.HTTP_404_NOT_FOUND)

        GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        ranked_earners = self._get_ranked_earners(badge, course_id)
        rank = self._get_current_user_rank(ranked_earners, user_uid)
        top_earners = ranked_earners[:self.MEMBERS_LIMIT]

        context = LeaderboardRetrievingContext(user_uid, signup_source, course_id)
        members_data = self._build_members_data(top_earners, course_id, context)

        response_data = {
            "badge": {
                "slug": badge.slug,
                "title": badge.title,
                "description": badge.description or "",
                "url": badge.image.url if badge.image else None,
            },
            "top10": members_data,
            "competitors": [],
            "rank": rank,
            "user_uid": user_uid,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def _get_ranked_earners(self, badge: Badge, course_id: Optional[str]) -> List[GammaUser]:
        """
        Provide badge earners ordered by their points in the descending order.
        """
        badge_content_type = ContentType.objects.get_for_model(Badge)
        achievements = (
            Achievement.objects
            .filter(content_type=badge_content_type, object_id=badge.id)
            .select_related("user")
            .prefetch_related("achievement_rules", "achievement_rules__rule")
        )

        earners = {}
        for achievement in achievements:
            if achievement.user.user_uid in earners:
                continue
            if is_achieved_badge(achievement, course_id):
                earners[achievement.user.user_uid] = achievement.user

        if not earners:
            return []

        earner_users = GammaUser.objects.filter(user_uid__in=earners.keys())
        if course_id:
            earner_users = earner_users.prefetch_related("courses_points")

        return sorted(
            earner_users,
            key=lambda gamma_user: self._member_points(gamma_user, course_id),
            reverse=True,
        )

    @staticmethod
    def _member_points(gamma_user: GammaUser, course_id: Optional[str]) -> int:
        """
        Provide the points used to rank a member.

        Course points are used when a course is requested, otherwise the user's
        total points (which match the general leaderboard score).
        """
        if not course_id:
            return gamma_user.points

        for course_points in gamma_user.courses_points.all():
            if course_points.course_id == course_id:
                return course_points.points
        return 0

    @staticmethod
    def _get_current_user_rank(ranked_earners: List[GammaUser], user_uid: Optional[str]) -> Optional[int]:
        """
        Provide the 1-based rank of the requesting user among all badge earners.
        """
        for index, gamma_user in enumerate(ranked_earners):
            if gamma_user.user_uid == user_uid:
                return index + 1
        return None

    def _build_members_data(
        self,
        earners: List[GammaUser],
        course_id: Optional[str],
        context: LeaderboardRetrievingContext,
    ) -> List[dict]:
        """
        Serialize earners into leaderboard member data with their points attached.
        """
        if not earners:
            return []

        user_uids = [gamma_user.user_uid for gamma_user in earners]
        members_data = ORMLeaderboardMemberDataRepository().get_leaderboard_members_data(user_uids, context)

        points_by_uid = {gamma_user.user_uid: self._member_points(gamma_user, course_id) for gamma_user in earners}
        for member_data in members_data:
            member_data["points"] = points_by_uid.get(member_data["user_uid"], 0)

        return members_data

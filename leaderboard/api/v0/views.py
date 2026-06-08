import math
from typing import List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievement
from badges.models import Badge
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

    It returns the badge's display data plus two flat, ranked lists (not a window
    around the requesting user): ``top10`` — the users who earned (completed) the
    badge, ranked by points; and ``in_progress`` — users with non-zero progress who
    have not completed it yet, ranked by their progress percentage. Both reuse the
    leaderboard member shape so the dashboard can render them with the regular
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

        ranked_earners, ranked_in_progress = self._collect_badge_members(badge, course_id)
        context = LeaderboardRetrievingContext(user_uid, signup_source, course_id)

        earners_data = self._build_members_data(ranked_earners[:self.MEMBERS_LIMIT], course_id, context)

        top_in_progress = ranked_in_progress[:self.MEMBERS_LIMIT]
        in_progress_data = self._build_members_data(
            [gamma_user for gamma_user, _ in top_in_progress], course_id, context
        )
        percent_by_uid = {gamma_user.user_uid: percent for gamma_user, percent in top_in_progress}
        for member_data in in_progress_data:
            member_data["progress_percent"] = percent_by_uid.get(member_data["user_uid"], 0)

        response_data = {
            "badge": {
                "slug": badge.slug,
                "title": badge.title,
                "description": badge.description or "",
                "url": badge.image.url if badge.image else None,
            },
            "top10": earners_data,
            "competitors": [],
            "rank": self._rank_of(user_uid, [gamma_user.user_uid for gamma_user in ranked_earners]),
            "in_progress": in_progress_data,
            "in_progress_rank": self._rank_of(
                user_uid, [gamma_user.user_uid for gamma_user, _ in ranked_in_progress]
            ),
            "user_uid": user_uid,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_badge_members(
        self, badge: Badge, course_id: Optional[str],
    ) -> Tuple[List[GammaUser], List[Tuple[GammaUser, int]]]:
        """
        Split the badge's users into earners and in-progress members.

        Earners (all rules completed) are returned ranked by points descending;
        in-progress members (not completed, but with progress above 0%) are
        returned as ``(user, percent)`` pairs ranked by their progress percentage
        descending, with points as a tie-breaker.
        """
        badge_content_type = ContentType.objects.get_for_model(Badge)
        achievements = (
            Achievement.objects
            .filter(content_type=badge_content_type, object_id=badge.id)
            .select_related("user")
            .prefetch_related("achievement_rules", "achievement_rules__rule")
        )

        earners = {}
        in_progress_percents = {}
        for achievement in achievements:
            user = achievement.user
            user_uid = user.user_uid

            if course_id and not achievement.get_course_related_achievement_rules(course_id):
                continue

            if achievement.all_rules_completed:
                earners[user_uid] = user
                in_progress_percents.pop(user_uid, None)
                continue

            if user_uid in earners:
                continue

            percent = self._progress_percent(achievement)
            if percent > 0 and percent > in_progress_percents.get(user_uid, 0):
                in_progress_percents[user_uid] = percent

        ranked_earners = sorted(
            self._fetch_users(earners.keys(), course_id),
            key=lambda gamma_user: self._member_points(gamma_user, course_id),
            reverse=True,
        )

        in_progress_users = self._fetch_users(in_progress_percents.keys(), course_id)
        ranked_in_progress = sorted(
            ((user, in_progress_percents[user.user_uid]) for user in in_progress_users),
            key=lambda pair: (pair[1], self._member_points(pair[0], course_id)),
            reverse=True,
        )
        return ranked_earners, ranked_in_progress

    @staticmethod
    def _fetch_users(user_uids, course_id: Optional[str]) -> List[GammaUser]:
        """
        Fetch GammaUsers for the given uids, prefetching course points when needed.
        """
        users = GammaUser.objects.filter(user_uid__in=list(user_uids))
        if course_id:
            users = users.prefetch_related("courses_points")
        return list(users)

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
    def _progress_percent(achievement: Achievement) -> int:
        """
        Compute a 0-100 progress percentage for an in-progress achievement.

        This mirrors the dashboard's ``calculateBadgeProgress`` exactly so the
        per-badge page and the dashboard badge widget never disagree: every event
        (across all of the achievement's rules) with a goal contributes
        ``floor((min(count, goal) / goal) * (100 / number_of_events))``, and these
        are summed. For example 35 of 1000 points -> floor(3.5) -> 3%.
        """
        events = [
            event_progress
            for rule_dependencies in (achievement.achievement_dependencies or [])
            if rule_dependencies
            for event_progress in rule_dependencies.get("events", {}).values()
            if event_progress.get("goal")
        ]
        if not events:
            return 0

        percentage_one_event = 100 / len(events)
        return sum(
            math.floor(min(event_progress.get("count", 0), event_progress["goal"]) / event_progress["goal"]
                       * percentage_one_event)
            for event_progress in events
        )

    @staticmethod
    def _rank_of(user_uid: Optional[str], ordered_user_uids: List[str]) -> Optional[int]:
        """
        Provide the 1-based position of ``user_uid`` within an ordered uid list.
        """
        for index, ordered_uid in enumerate(ordered_user_uids):
            if ordered_uid == user_uid:
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

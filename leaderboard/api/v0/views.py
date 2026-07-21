import math
from typing import List, Optional, Set, Tuple

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from achievements.models import Achievement
from badges.models import Badge
from core.authentication import KeySecretAuthentication
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.instructors import get_instructor_user_uids, is_instructor_badge_slug
from leaderboard.repository import ORMLeaderboardMemberDataRepository, RedisLeaderboardRepository
from leaderboard.usecases import GetPersonalizedLeaderboardUseCase
from users.models import GammaUser, GammaUserCoursePoints

TRUE_VALUES = {"1", "true", "yes", "on"}


def _is_true(value: Optional[str]) -> bool:
    """
    Whether a request parameter carries an affirmative value.
    """
    return str(value).strip().lower() in TRUE_VALUES


def _hidden_user_uids(hide_instructors: bool) -> Set[str]:
    """
    Provide the users to leave off the board for this request.

    Empty unless the caller asked for the instructor-free view, so the default board
    costs exactly what it did before.
    """
    return get_instructor_user_uids() if hide_instructors else set()


def _standard_competition_rank(
    user_uid: Optional[str],
    ranked_members: List[Tuple[str, float]],
) -> Optional[int]:
    """
    Provide the 1-based standard-competition ("1224") rank of ``user_uid``.

    ``ranked_members`` is the leaderboard ordered best-first as ``(uid, value)``
    pairs, where ``value`` is whatever the board is ranked by (points, or progress
    percentage). Members sharing the same value share a rank and the next distinct
    value resumes after the gap, so two learners tied on grade get the same number —
    matching how the dashboard numbers the rows. Returns ``None`` when the user is
    absent (e.g. the viewer is not on this board).
    """
    member_value = None
    found = False
    for uid, value in ranked_members:
        if uid == user_uid:
            member_value = value
            found = True
            break

    if not found:
        return None

    return sum(1 for _, value in ranked_members if value > member_value) + 1


class LeaderBoardView(APIView):
    """
    Provide personalized leaderboard data for the requesting Gamma user.

    ``hide_instructors=1`` serves the same board with instructors left off it and every
    rank recomputed accordingly (see :mod:`leaderboard.instructors`).
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request):
        user_uid = request.GET.get("username")
        gamma_user = GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        leaderboard_retrieving_context = LeaderboardRetrievingContext(
            user_uid,
            request.GET.get("signup_source"),
            request.GET.get("course_id"),
            is_excluded=gamma_user.excluded_from_leaderboard,
        )

        hidden_user_uids = _hidden_user_uids(_is_true(request.GET.get("hide_instructors")))
        response_data = self._collect_response_data(leaderboard_retrieving_context, hidden_user_uids)

        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_response_data(
        self,
        leaderboard_retrieving_context: LeaderboardRetrievingContext,
        hidden_user_uids: Set[str],
    ) -> dict:
        """
        Collect data to place in the response body.
        """
        redis_leaderboard_repository = RedisLeaderboardRepository()
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        leaders, competitors, rank = GetPersonalizedLeaderboardUseCase(
            redis_leaderboard_repository,
            leaderboard_member_data_repository,
            hidden_user_uids=hidden_user_uids,
        ).execute(leaderboard_retrieving_context)

        return {
            "top10": leaders,
            "rank": rank,
            "user_uid": leaderboard_retrieving_context.user_uid,
            "competitors": competitors,
            # The viewer is an instructor looking at the instructor-free board: they have
            # no place on it, so the dashboard must not append its "you are not ranked
            # yet" row for them (that row is for a learner who has yet to score).
            "viewer_hidden": leaderboard_retrieving_context.user_uid in hidden_user_uids,
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

        # Deactivated (draft) badges have no leaderboard: they are hidden from every
        # learner-facing surface, so a direct URL to their board 404s like a deleted one.
        badge = Badge.objects.filter(slug=badge_slug, is_active=True).order_by("pk").first()
        if badge is None:
            return Response({"error": "Accomplishment not found."}, status=status.HTTP_404_NOT_FOUND)

        GammaUser.ensure_gamma_user_is_created(user_uid=user_uid)

        # An instructor badge's own board is the one place hiding instructors makes no
        # sense: it would empty the page. The board is served unfiltered there and the
        # dashboard drops the toggle, rather than honouring a sticky preference into a
        # blank list.
        is_instructor_badge = is_instructor_badge_slug(badge.slug)
        hidden_user_uids = _hidden_user_uids(
            _is_true(request.GET.get("hide_instructors")) and not is_instructor_badge
        )

        ranked_earners, ranked_in_progress = self._collect_badge_members(badge, course_id, hidden_user_uids)
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
                # Free-text grouping label, echoed so the board can link back to this
                # badge's section of the All Accomplishments page. Blank for badges
                # that were never categorised, which the dashboard renders as no link.
                "category": badge.category or "",
                "description": badge.description or "",
                "url": badge.image.url if badge.image else None,
                "is_instructor_badge": is_instructor_badge,
            },
            "top10": earners_data,
            "competitors": [],
            "rank": _standard_competition_rank(
                user_uid,
                [(gamma_user.user_uid, self._member_points(gamma_user, course_id)) for gamma_user in ranked_earners],
            ),
            "in_progress": in_progress_data,
            "in_progress_rank": _standard_competition_rank(
                user_uid,
                [(gamma_user.user_uid, percent) for gamma_user, percent in ranked_in_progress],
            ),
            "user_uid": user_uid,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def _collect_badge_members(
        self, badge: Badge, course_id: Optional[str], hidden_user_uids: Optional[Set[str]] = None,
    ) -> Tuple[List[GammaUser], List[Tuple[GammaUser, int]]]:
        """
        Split the badge's users into earners and in-progress members.

        Earners (all rules completed) are returned ranked by points descending;
        in-progress members (not completed, but with progress above 0%) are
        returned as ``(user, percent)`` pairs ranked by their progress percentage
        descending, with points as a tie-breaker.

        ``hidden_user_uids`` are dropped before ranking, so the ranks and the 100-member
        cut-off are both computed over the members that are actually shown.
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
            self._fetch_users(earners.keys(), course_id, hidden_user_uids),
            key=lambda gamma_user: self._member_points(gamma_user, course_id),
            reverse=True,
        )

        in_progress_users = self._fetch_users(in_progress_percents.keys(), course_id, hidden_user_uids)
        ranked_in_progress = sorted(
            ((user, in_progress_percents[user.user_uid]) for user in in_progress_users),
            key=lambda pair: (pair[1], self._member_points(pair[0], course_id)),
            reverse=True,
        )
        return ranked_earners, ranked_in_progress

    @staticmethod
    def _fetch_users(
        user_uids, course_id: Optional[str], hidden_user_uids: Optional[Set[str]] = None,
    ) -> List[GammaUser]:
        """
        Fetch GammaUsers for the given uids, prefetching course points when needed.

        Opted-out users are dropped so they never appear on a per-badge leaderboard, as
        are the members hidden by the view currently requested.
        """
        users = GammaUser.objects.filter(user_uid__in=list(user_uids)).exclude(
            excluded_from_leaderboard=True
        )
        if hidden_user_uids:
            users = users.exclude(user_uid__in=list(hidden_user_uids))
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


class CoursePointsView(APIView):
    """
    Return per-course points for a given set of users.

    The dashboard's course leaderboard uses this to rank certificate-earners by
    their course points; the dashboard runs inside the LMS and cannot query the
    Gamma database directly.
    """

    authentication_classes = (KeySecretAuthentication,)

    def post(self, request):
        course_id = request.data.get("course_id")
        user_uids = request.data.get("user_uids") or []

        if not course_id or not user_uids:
            return Response({}, status=status.HTTP_200_OK)

        points_by_uid = dict(
            GammaUserCoursePoints.objects
            .filter(course_id=course_id, gamma_user__user_uid__in=user_uids)
            .values_list("gamma_user__user_uid", "points")
        )
        return Response(points_by_uid, status=status.HTTP_200_OK)


class UsersLeaderBoardView(APIView):
    """
    Provide a leaderboard restricted to an explicit set of users, ranked by points.

    The dashboard runs inside the LMS and resolves *which* users share a trait that
    only it can see (e.g. a publicly-shared profile country); Gamma cannot see that
    trait, so the dashboard passes the candidate ``user_uids`` here and Gamma ranks
    just those users by their general-leaderboard points. The response matches the
    regular leaderboard shape (``top10``/``competitors``/``rank``/``user_uid``) so the
    dashboard can enrich and render it with the existing leaderboard components.

    ``user_uids`` is sent in the POST body rather than the query string because the
    candidate set can be large (every learner from a populous country), exactly like
    :class:`CoursePointsView`.
    """

    authentication_classes = (KeySecretAuthentication,)

    MEMBERS_LIMIT = 100

    def post(self, request):
        viewer_uid = request.data.get("username")
        signup_source = request.data.get("signup_source")
        user_uids = request.data.get("user_uids") or []

        if not user_uids:
            return self._empty_response(viewer_uid)

        hidden_user_uids = _hidden_user_uids(_is_true(request.data.get("hide_instructors")))
        ranked_users = self._rank_users(user_uids, signup_source, hidden_user_uids)

        context = LeaderboardRetrievingContext(viewer_uid, signup_source, None)
        members_data = self._build_members_data(ranked_users[:self.MEMBERS_LIMIT], context)

        return Response(
            {
                "top10": members_data,
                "competitors": [],
                "rank": _standard_competition_rank(
                    viewer_uid,
                    [(gamma_user.user_uid, gamma_user.points) for gamma_user in ranked_users],
                ),
                "user_uid": viewer_uid,
                "viewer_hidden": viewer_uid in hidden_user_uids,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _empty_response(viewer_uid: Optional[str]) -> Response:
        """
        Shape returned when no candidate users were supplied (e.g. nobody in the
        country shares it publicly): an empty, well-formed leaderboard.
        """
        return Response(
            {"top10": [], "competitors": [], "rank": None, "user_uid": viewer_uid, "viewer_hidden": False},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _rank_users(
        user_uids: List[str], signup_source: Optional[str], hidden_user_uids: Optional[Set[str]] = None,
    ) -> List[GammaUser]:
        """
        Fetch the requested users that belong to ``signup_source``'s leaderboard,
        ordered by total points (descending).

        Scoping by signup source — with the same ``None``/empty -> ``MAIN_SIGNUP_SOURCE``
        normalization the leaderboard-building code uses — keeps this page consistent
        with the regular (per-signup-source) leaderboard: it shows the same population,
        just narrowed to the supplied users.
        """
        effective_source = signup_source or settings.MAIN_SIGNUP_SOURCE
        # Opted-out users are dropped here, so they never appear on the per-country or
        # per-course "Completed" leaderboards (and an opted-out viewer gets rank=None).
        # The members hidden by the requested view go the same way, before ranking, so
        # the ranks close up rather than leaving gaps where they were.
        users = GammaUser.objects.filter(user_uid__in=user_uids).exclude(excluded_from_leaderboard=True)

        if hidden_user_uids:
            users = users.exclude(user_uid__in=list(hidden_user_uids))

        if effective_source == settings.MAIN_SIGNUP_SOURCE:
            users = users.filter(
                Q(signup_source=effective_source) | Q(signup_source__isnull=True) | Q(signup_source="")
            )
        else:
            users = users.filter(signup_source=effective_source)

        return sorted(users, key=lambda gamma_user: gamma_user.points, reverse=True)

    @staticmethod
    def _build_members_data(ranked_users: List[GammaUser], context: LeaderboardRetrievingContext) -> List[dict]:
        """
        Serialize the (already ranked) users into leaderboard member data with their
        points attached, preserving the ranked order.
        """
        if not ranked_users:
            return []

        ranked_uids = [gamma_user.user_uid for gamma_user in ranked_users]
        members_data = ORMLeaderboardMemberDataRepository().get_leaderboard_members_data(ranked_uids, context)

        points_by_uid = {gamma_user.user_uid: gamma_user.points for gamma_user in ranked_users}
        for member_data in members_data:
            member_data["points"] = points_by_uid.get(member_data["user_uid"], 0)

        return members_data


class InstructorUserUidsView(APIView):
    """
    List the user_uids of everyone holding an instructor badge.

    The dashboard uses this for the one leaderboard section it ranks itself — the
    per-course "In progress" list, ranked by course grade rather than points, which
    Gamma never sees. Every point-ranked section is filtered by Gamma directly.
    """

    authentication_classes = (KeySecretAuthentication,)

    def get(self, request, *args, **kwargs):
        return Response({"user_uids": sorted(get_instructor_user_uids())})

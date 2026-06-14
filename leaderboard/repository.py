import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple

from django.db.models import Prefetch

from achievements.models import AchievementRule
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.entity import LeaderboardMember, UserLeaderboardsData
from leaderboard.serializers import LeaderboardMemberSerializer
from leaderboard.utils import get_redis_client
from rules.models import Rule
from users.models import GammaUser

logger = logging.getLogger(__name__)


class LeaderboardRepository(ABC):
    """
    Abstract base class for leaderboard data management.
    """

    @abstractmethod
    def get_or_init_user_score(self, user_uid: str, leaderboard_id: str) -> float:
        """
        Provide the leaderboard user score.

        If the user is not in the leaderboard, add him to the leaderboard with
        score 0.
        """

    def get_user_count_with_score_gt(self, value: int, leaderboard_id: str) -> int:
        """
        Provide the count of leaderboard members with score greater than value.
        """

    @abstractmethod
    def get_users_with_highest_score(self, count: int, leaderboard_id: str) -> List[LeaderboardMember]:
        """
        Provide a specified count of leaderboard members with the highest score.

        The users are ordered by their score in the descending order.
        """

    @abstractmethod
    def get_top_users_with_score_gt(self, value: int, leaderboard_id: str) -> List[LeaderboardMember]:
        """
        Provide leaderboard members with score greater than the provided value.

        The users are ordered by their score in the descending order.
        """

    def get_nearest_top_users_with_score_gt(
        self,
        value: int,
        limit: int,
        leaderboard_id: str,
    ) -> List[LeaderboardMember]:
        """
        Provide leaderboard members with score greater than the provided value.

        If the number of found users exceeds the limit value, only the users
        whose score is closest to the specified value are returned in the
        corresponding score descending order.
        """

    @abstractmethod
    def get_top_users_with_score_lte(
        self,
        value: int,
        limit: int,
        leaderboard_id: str,
        users_to_exclude: Optional[Set[str]] = None,
    ):
        """
        Provide leaderboard members with score less or equal the provided value.

        If the number of found users exceeds the limit value, only the users
        whose score is closest to the specified value are returned in the
        corresponding score descending order.
        """

    @abstractmethod
    def add_leaderboard_data(self, data: Dict[str, int], leaderboard_id: str) -> None:
        """
        Add the users and their scores to the leaderboard.

        If a user is already present in the leaderboard, their score is updated
        to the provided value.
        """

    @abstractmethod
    def remove_user_from_leaderboard(self, user_uid: str, leaderboard_id: str) -> None:
        """
        Remove user from the specified leaderboard.
        """


class RedisLeaderboardRepository(LeaderboardRepository):
    """
    Repository that manages leaderboard data in Redis.
    """

    def __init__(self):
        self._redis_client = get_redis_client()

    def get_or_init_user_score(self, user_uid: str, leaderboard_id: str) -> float:
        score = self._redis_client.zscore(leaderboard_id, user_uid)
        if score is None:
            self._redis_client.zadd(leaderboard_id, {user_uid: 0})
            logger.info(
                f'User "{user_uid}" was not in the leaderboard "{leaderboard_id}", so he is added to the leaderboard '
                "with score 0."
            )
            return 0.
        return score

    def get_user_count_with_score_gt(self, value: int, leaderboard_id: str) -> int:
        return self._redis_client.zcount(leaderboard_id, f"({value}", "+inf")

    def get_users_with_highest_score(self, count: int, leaderboard_id: str) -> List[LeaderboardMember]:
        return [
            self._convert_to_leaderboard_member(item)
            for item in self._redis_client.zrevrange(leaderboard_id, 0, count - 1, withscores=True)
        ]

    def get_top_users_with_score_gt(self, value: int, leaderboard_id: str) -> List[LeaderboardMember]:
        return [
            self._convert_to_leaderboard_member(item)
            for item in self._redis_client.zrevrangebyscore(leaderboard_id, "+inf", f"({value}", withscores=True)
        ]

    def get_nearest_top_users_with_score_gt(
        self,
        value: int,
        limit: int,
        leaderboard_id: str,
    ) -> List[LeaderboardMember]:
        leaderboard_data_items = list(reversed(self._redis_client.zrangebyscore(
            leaderboard_id, f"({value}", "+inf", withscores=True, start=0, num=limit
        )))
        return [self._convert_to_leaderboard_member(item) for item in leaderboard_data_items]

    def get_top_users_with_score_lte(
        self,
        value: int,
        limit: int,
        leaderboard_id: str,
        users_to_exclude: Optional[Set[str]] = None,
    ):
        leaderboard_data_items = self._redis_client.zrevrangebyscore(
            leaderboard_id,
            value,
            "-inf",
            withscores=True,
            start=0,
            num=limit,
        )

        leaderboard_members = [self._convert_to_leaderboard_member(item) for item in leaderboard_data_items]

        if users_to_exclude:
            leaderboard_members = [member for member in leaderboard_members if member.user_uid not in users_to_exclude]

        return leaderboard_members

    def add_leaderboard_data(self, data: Dict[str, int], leaderboard_id: str) -> None:
        if data:
            self._redis_client.zadd(leaderboard_id, data)

    def remove_user_from_leaderboard(self, user_uid: str, leaderboard_id: str) -> None:
        self._redis_client.zrem(leaderboard_id, user_uid)

    @staticmethod
    def _convert_to_leaderboard_member(data: Tuple[str, float]) -> LeaderboardMember:
        """
        Convert the username-score pair into a LeaderboardMember instance.
        """
        return LeaderboardMember({"user_uid": data[0].decode("utf-8"), "points": data[1]})


class LeaderboardsPendingUpdateRepository(ABC):
    """
    Abstract base class for scheduling user leaderboards' updating data management.
    """

    @abstractmethod
    def schedule_user_leaderboards_update(self, user_uid: str) -> None:
        """
        Schedule user leaderboards' data updating.
        """

    @abstractmethod
    def pop_users_with_pending_leaderboards_update(self) -> Set[str]:
        """
        Provide users who were scheduled to update their leaderboards' data.

        Delete the current users from the scheduling queue.
        """


class RedisLeaderboardsPendingUpdateRepository(LeaderboardsPendingUpdateRepository):
    """
    Repository that manages user leaderboards' updating scheduling in Redis.
    """

    CACHE_KEY = "pending_leaderboard_update"

    def __init__(self) -> None:
        self._redis_client = get_redis_client()

    def schedule_user_leaderboards_update(self, user_uid: str) -> None:
        self._redis_client.sadd(self.CACHE_KEY, user_uid)

    def pop_users_with_pending_leaderboards_update(self) -> Set[str]:
        pipe = self._redis_client.pipeline()
        pipe.smembers(self.CACHE_KEY)
        pipe.delete(self.CACHE_KEY)
        users_with_pending_leaderboards_update, __ = pipe.execute()
        return {user_uid.decode("utf-8") for user_uid in users_with_pending_leaderboards_update}


class LeaderboardMemberDataRepository(ABC):
    """
    Abstract base class for leaderboard member related data management.
    """

    @abstractmethod
    def get_user_count(self) -> int:
        """
        Provide the number of users that can potentially be leaderboard members.
        """

    @abstractmethod
    def get_leaderboard_members_data(
        self,
        user_uids: List[str],
        leaderboard_retrieving_context: LeaderboardRetrievingContext,
    ) -> List[dict]:
        """
        Provide additional data related to the leaderboard members.
        """

    @abstractmethod
    def collect_user_leaderboards_data(
        self,
        _filters: Optional[dict] = None,
        offset: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> List[UserLeaderboardsData]:
        """
        Provide user data required for leaderboards building.
        """


class ORMLeaderboardMemberDataRepository(LeaderboardMemberDataRepository):
    """
    Repository that manages leaderboard member related data in Django ORM.
    """

    def get_user_count(self) -> int:
        return GammaUser.objects.count()

    def get_leaderboard_members_data(
        self,
        user_uids: List[str],
        leaderboard_retrieving_context: LeaderboardRetrievingContext,
    ) -> List[dict]:
        leaderboard_members = (
            GammaUser.objects.filter(user_uid__in=user_uids)
            .prefetch_related(
                "achievement_set__content_type",
                "achievement_set__content_object",
                Prefetch("achievement_set__achievement_rules", queryset=AchievementRule.objects.order_by("pk")),
                Prefetch("achievement_set__achievement_rules__rule", queryset=Rule.objects.order_by("pk")),
            )
        )

        serializer = LeaderboardMemberSerializer(
            leaderboard_members,
            context={"leaderboard_retrieving_context": leaderboard_retrieving_context},
            many=True,
        )
        leaderboard_members_data = serializer.data
        leaderboard_members_data.sort(key=lambda data_item: user_uids.index(data_item["user_uid"]))
        return leaderboard_members_data

    def collect_user_leaderboards_data(
        self,
        _filters: Optional[dict] = None,
        offset: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> List[UserLeaderboardsData]:
        # Opted-out users are never placed on any leaderboard: excluding them here keeps
        # them out of both the full initialization and the per-user update (this feeds the
        # general + course Redis leaderboards), so the pipeline never (re-)adds them.
        queryset = GammaUser.objects.exclude(excluded_from_leaderboard=True).prefetch_related("courses_points")

        if _filters:
            queryset = queryset.filter(**_filters)

        queryset = queryset.order_by("pk")

        if offset is not None and batch_size is not None:
            queryset = queryset[offset:offset + batch_size]

        return [self._build_user_leaderboards_data(item) for item in queryset]

    @staticmethod
    def _build_user_leaderboards_data(gamma_user: GammaUser) -> UserLeaderboardsData:
        """
        Build user leaderboards data from a GammaUser and its relations.
        """
        return UserLeaderboardsData({
            "user_uid": gamma_user.user_uid,
            "points": gamma_user.points,
            "signup_source": gamma_user.signup_source,
            "courses_points": {
                course_points.course_id: course_points.points
                for course_points in gamma_user.courses_points.all()
            },
        })

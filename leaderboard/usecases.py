import logging
from collections import defaultdict
from typing import Callable, Dict, Generator, List, Optional, Tuple

from django.conf import settings

from leaderboard.constants import (
    COURSE_LEADERBOARD_ID_TEMPLATE,
    GENERAL_LEADERBOARD_ID_TEMPLATE,
    LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY,
)
from leaderboard.dataclasses import LeaderboardRetrievingContext
from leaderboard.entity import LeaderboardMember, UserLeaderboardsData
from leaderboard.enums import LeaderboardsInitializationStatus
from leaderboard.repository import (
    LeaderboardMemberDataRepository,
    LeaderboardRepository,
    LeaderboardsPendingUpdateRepository,
)
from leaderboard.utils import get_leaderboards_initialization_status, get_redis_client

logger = logging.getLogger(__name__)


class GetPersonalizedLeaderboardUseCase:
    """
    Use case for getting personalized leaderboard data.

    As leaderboard contains data about a large number of its members, this
    use case allows getting only relevant to user leaderboard data.

    The provided data:
    - top 10 users.
    - competitors:
        - 4 users before and 2 users after current user,
        when the user is not in the top 10 and does not occupy the last 2 positions.
        - 5 users before and 1 users after current user,
        when the user possesses the second to last position in the rating.
        - 6 users before and 0 users after current user,
        when the user possesses to last position in the leaderboard, but he has points.
        - An empty list if the user has no points, or the user is in the top 10.
    - current user rank.
    """

    TAIL_COMPETITORS_LIMIT = 2

    def __init__(
        self,
        leaderboard_repository: LeaderboardRepository,
        leaderboard_member_data_repository: LeaderboardMemberDataRepository,
    ) -> None:
        self._leaderboard_repository = leaderboard_repository
        self._leaderboard_member_data_repository = leaderboard_member_data_repository

    def execute(self, context: LeaderboardRetrievingContext) -> Tuple[List[dict], List[dict], Optional[int]]:
        user_uid = context.user_uid
        leaderboard_id = context.leaderboard_id
        current_user_score = self._leaderboard_repository.get_or_init_user_score(user_uid, leaderboard_id)
        current_user = LeaderboardMember({"user_uid": user_uid, "points": current_user_score})

        rank = self._get_user_rank(current_user, leaderboard_id)
        top10_members_data = self._get_top10_members_data(current_user, rank, context)

        competitors_data = []
        if current_user.points == 0:
            rank = None
            return top10_members_data, competitors_data, rank

        if rank > 10:
            tail_competitors = self._get_tail_competitors(current_user, leaderboard_id)
            head_competitors_limit = 6 - len(tail_competitors)
            head_competitors = self._get_head_competitors(current_user, head_competitors_limit, leaderboard_id)
            competitors = head_competitors + [current_user] + tail_competitors
            competitors_data = self._build_leaderboard_members_data(competitors, context)
        return top10_members_data, competitors_data, rank

    def _get_user_rank(self, current_user: LeaderboardMember, leaderboard_id: str) -> int:
        """
        Determining the current position of the user based on number of points.

        In case of a tie in points with other users, the current user always ranks higher.
        """
        return self._leaderboard_repository.get_user_count_with_score_gt(current_user.points, leaderboard_id) + 1

    def _get_top10_members_data(
        self,
        current_user: LeaderboardMember,
        rank: int,
        context: LeaderboardRetrievingContext,
    ) -> List[dict]:
        """
        Provide top 10 leaderboard members data.
        """
        leaderboard_id = context.leaderboard_id
        current_user_points = current_user.points

        if rank > 10:
            top10_members = self._leaderboard_repository.get_users_with_highest_score(10, leaderboard_id)
            return self._build_leaderboard_members_data(top10_members, context)

        head_top10_members = self._leaderboard_repository.get_top_users_with_score_gt(
            current_user_points,
            leaderboard_id,
        )

        if current_user_points == 0:
            return self._build_leaderboard_members_data(head_top10_members, context)

        head_top10_length = len(head_top10_members)
        if head_top10_length == 9:
            head_top10_members.append(current_user)
            return self._build_leaderboard_members_data(head_top10_members, context)

        tail_top10_members = self._leaderboard_repository.get_top_users_with_score_lte(
            current_user_points,
            10 - head_top10_length,
            leaderboard_id,
            users_to_exclude={current_user.user_uid},
        )

        top10_members = (head_top10_members + [current_user] + tail_top10_members)[:10]
        return self._build_leaderboard_members_data(top10_members, context)

    def _get_head_competitors(
        self,
        current_user: LeaderboardMember,
        limit: int,
        leaderboard_id: str,
    ) -> List[LeaderboardMember]:
        """
        Provide the user competitors with higher score.
        """
        return self._leaderboard_repository.get_nearest_top_users_with_score_gt(
            current_user.points,
            limit,
            leaderboard_id,
        )

    def _get_tail_competitors(self, current_user: LeaderboardMember, leaderboard_id: str) -> List[LeaderboardMember]:
        """
        Provide the user competitors with lower score.
        """
        return self._leaderboard_repository.get_top_users_with_score_lte(
            current_user.points,
            self.TAIL_COMPETITORS_LIMIT + 1,
            leaderboard_id,
            users_to_exclude={current_user.user_uid},
        )[:self.TAIL_COMPETITORS_LIMIT]

    def _build_leaderboard_members_data(
        self,
        leaderboard_members: List[LeaderboardMember],
        context: LeaderboardRetrievingContext,
    ) -> List[dict]:
        """
        Provide user data required to display them on the leaderboard.
        """
        leaderboard_members_user_uuids = [member.user_uid for member in leaderboard_members]
        leaderboard_members_data = self._leaderboard_member_data_repository.get_leaderboard_members_data(
            leaderboard_members_user_uuids,
            context,
        )

        for member, member_data in zip(leaderboard_members, leaderboard_members_data):
            member_data["points"] = member.points

        return leaderboard_members_data


class EnqueueLeaderboardsUpdateUseCase:
    """
    Use case for adding a user to leaderboards' updating scheduling queue.
    """

    def __init__(self, repository: LeaderboardsPendingUpdateRepository) -> None:
        self._repository = repository

    def execute(self, user_uid: str) -> None:
        if get_leaderboards_initialization_status() == LeaderboardsInitializationStatus.COMPLETED:
            self._repository.schedule_user_leaderboards_update(user_uid)
            logger.info(f"Leaderboards updating is scheduled for user {user_uid!r}.")
        else:
            logger.info(
                f"Leaderboards updating is not scheduled for user {user_uid!r} because leaderboards are not "
                "initialized or their initialization is in progress."
            )


class ScheduleLeaderboardsInitializationUseCase:
    """
    Use case for scheduling leaderboards' initialization tasks batches.

    Divide all gamma users into batches and run tasks for initialization their
    leaderboards data.
    """

    def __init__(self, leaderboard_member_data_repository: LeaderboardMemberDataRepository) -> None:
        self._leaderboard_member_data_repository = leaderboard_member_data_repository

    def execute(self, batch_size: int) -> None:
        if get_leaderboards_initialization_status() == LeaderboardsInitializationStatus.IN_PROGRESS:
            logger.warning("Leaderboards initialization is not scheduled because it's already in progress.")
            return

        logger.info("Leaderboards initialization scheduling is started.")

        users_count = self._leaderboard_member_data_repository.get_user_count()
        redis_client = get_redis_client()
        batches_count = users_count // batch_size + bool(users_count % batch_size)
        redis_client.set(LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY, batches_count)

        from leaderboard.tasks import task_initialize_leaderboards

        for options in self._generate_tasks_options(users_count, batch_size):
            task_initialize_leaderboards.delay(*options)
            logger.info(f"Leaderboards initialization task is scheduled with arguments {options}.")

        logger.info("Leaderboards initialization scheduling is finished.")

    def _generate_tasks_options(self, users_count: int, batch_size: int) -> Generator[Tuple[int, int], None, None]:
        """
        Generate options for user leaderboards data initialization tasks.
        """
        for offset in range(0, users_count, batch_size):
            yield (offset, batch_size)


class LeaderboardsBuildingService:
    """
    Perform leaderboards building.

    Add data about users to leaderboards related to them.
    """

    def __init__(self, leaderboard_repository: LeaderboardRepository) -> None:
        self._leaderboard_repository = leaderboard_repository

    def build_all_leaderboards(self, leaderboards_data: List[UserLeaderboardsData]) -> None:
        """
        Run all leaderboards building.
        """
        for leaderboards_builder in self.get_leaderboards_builders():
            leaderboards_builder(leaderboards_data)

    def get_leaderboards_builders(self) -> Tuple[Callable[[List[UserLeaderboardsData]], None], ...]:
        """
        Provide methods responsible for a leaderboard building.
        """
        return (self.build_general_leaderboards, self.build_course_leaderboards)

    def build_general_leaderboards(self, leaderboards_data: List[UserLeaderboardsData]) -> None:
        """
        Run all platform-wide leaderboards building.

        General leaderboards contain data about all platform users.
        """
        general_leaderboards_data = self._build_general_leaderboards_data(leaderboards_data)

        for signup_source, leaderboard_data in general_leaderboards_data.items():
            leaderboard_id = GENERAL_LEADERBOARD_ID_TEMPLATE.format(user_signup_source=signup_source)
            self._leaderboard_repository.add_leaderboard_data(leaderboard_data, leaderboard_id)

    def _build_general_leaderboards_data(
        self,
        leaderboards_data: List[UserLeaderboardsData],
    ) -> Dict[str, Dict[str, int]]:
        """
        Build signup source to related leaderboard data mapping.
        """
        general_leaderboards_data = defaultdict(dict)

        for data_item in leaderboards_data:
            signup_source = data_item.signup_source
            user_uid = data_item.user_uid
            general_leaderboards_data[signup_source][user_uid] = data_item.points

        general_leaderboards_data[settings.MAIN_SIGNUP_SOURCE].update(
            general_leaderboards_data.pop(None, {})
        )

        return general_leaderboards_data

    def build_course_leaderboards(self, leaderboards_data: List[UserLeaderboardsData]) -> None:
        """
        Run course-wide leaderboards building.

        Course leaderboards contain data only about users that earned points
        for course activities.
        """
        courses_leaderboards_data = self._build_courses_leaderboards_data(leaderboards_data)

        for signup_source, signup_source_leaderboards_data in courses_leaderboards_data.items():
            for course_id, leaderboard_data in signup_source_leaderboards_data.items():
                leaderboard_id = COURSE_LEADERBOARD_ID_TEMPLATE.format(
                    user_signup_source=signup_source,
                    course_id=course_id,
                )
                self._leaderboard_repository.add_leaderboard_data(leaderboard_data, leaderboard_id)

    def _build_courses_leaderboards_data(
        self,
        leaderboards_data: List[UserLeaderboardsData],
    ) -> Dict[str, Dict[str, Dict[str, int]]]:
        """
        Build signup source to course ID to related leaderboard data mapping.
        """
        courses_leaderboards_data = defaultdict(lambda: defaultdict(dict))

        for data_item in leaderboards_data:
            signup_source = data_item.signup_source
            user_uid = data_item.user_uid

            for course_id, points in data_item.courses_points.items():
                courses_leaderboards_data[signup_source][course_id][user_uid] = points

        courses_leaderboards_data[settings.MAIN_SIGNUP_SOURCE].update(
            courses_leaderboards_data.pop(None, {})
        )

        return courses_leaderboards_data


class InitializeLeaderboardsUseCase:
    """
    Use case for leaderboards data initialization.

    Take data about user batch (offset and batch size) and initialize the
    corresponding users data in leaderboards.
    """

    def __init__(
        self,
        leaderboard_repository: LeaderboardRepository,
        leaderboard_member_data_repository: LeaderboardMemberDataRepository,
    ) -> None:
        self._leaderboard_repository = leaderboard_repository
        self._leaderboard_member_data_repository = leaderboard_member_data_repository

    def execute(self, offset: int, batch_size: int) -> None:
        logger.info(
            f'Leaderboards initialization for user batch with batch size "{batch_size}" and offset "{offset}" is '
            "started."
        )

        leaderboards_data = self._leaderboard_member_data_repository.collect_user_leaderboards_data(
            offset=offset,
            batch_size=batch_size,
        )

        LeaderboardsBuildingService(self._leaderboard_repository).build_all_leaderboards(leaderboards_data)

        redis_client = get_redis_client()
        batches_left = redis_client.decr(LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY)
        logger.info(
            f'Leaderboards initialization for user batch with batch size "{batch_size}" and offset "{offset}" is '
            f"finished. Batches left: {batches_left}."
        )


class ResetLeaderboardsInitializationStatusUseCase:
    """
    Reset leaderboards initialization status to "Not started".

    It is useful for the cases when the leaderboards initialization is failed,
    and we want to re-run it.
    As the leaderboards initialization status depends on a cache value and
    a failure can potentially lead to an inconsistent cache value state, it
    could be necessary to reset this cache value before trying an initialization
    process again.
    """

    def execute(self) -> None:
        redis_client = get_redis_client()
        redis_client.delete(LEADERBOARDS_INITIALIZATION_BATCHES_LEFT_COUNT_CACHE_KEY)
        logger.info('Leaderboards initialization status is set to "Not started.')


class UpdateLeaderboardsUseCase:
    """
    Update the leaderboards data for users pending to update.
    """

    def __init__(
        self,
        leaderboard_repository: LeaderboardRepository,
        leaderboard_member_data_repository: LeaderboardMemberDataRepository,
        leaderboards_pending_update_repository: LeaderboardsPendingUpdateRepository,
    ) -> None:
        self._leaderboard_repository = leaderboard_repository
        self._leaderboard_member_data_repository = leaderboard_member_data_repository
        self._leaderboards_pending_update_repository = leaderboards_pending_update_repository

    def execute(self) -> None:
        if get_leaderboards_initialization_status() != LeaderboardsInitializationStatus.COMPLETED:
            logger.info(
                "Leaderboards updating is not started because leaderboards are not initialized or their "
                "initialization is in progress."
            )
            return

        user_uids = self._leaderboards_pending_update_repository.pop_users_with_pending_leaderboards_update()
        leaderboards_data = self._leaderboard_member_data_repository.collect_user_leaderboards_data(
            _filters={"user_uid__in": user_uids},
        )

        logger.info(f"Leaderboards updating is started for Gamma users {user_uids}.")
        LeaderboardsBuildingService(self._leaderboard_repository).build_all_leaderboards(leaderboards_data)
        logger.info(f"Leaderboards updating is finished for Gamma users {user_uids}.")

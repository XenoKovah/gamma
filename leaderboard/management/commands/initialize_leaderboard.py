from django.conf import settings
from django.core.management.base import BaseCommand

from leaderboard.repository import ORMLeaderboardMemberDataRepository
from leaderboard.usecases import ScheduleLeaderboardsInitializationUseCase


class Command(BaseCommand):
    """
    Perform scheduling leaderboards initialization.
    """

    def handle(self, *args, **options) -> None:
        leaderboard_member_data_repository = ORMLeaderboardMemberDataRepository()
        ScheduleLeaderboardsInitializationUseCase(
            leaderboard_member_data_repository,
        ).execute(settings.LEADERBOARD_INITIALIZATION_BATCH_SIZE)

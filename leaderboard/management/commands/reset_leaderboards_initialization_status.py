from django.core.management.base import BaseCommand

from leaderboard.usecases import ResetLeaderboardsInitializationStatusUseCase


class Command(BaseCommand):
    """
    Perform leaderboards initialization status resetting.
    """

    def handle(self, *args, **options) -> None:
        ResetLeaderboardsInitializationStatusUseCase().execute()

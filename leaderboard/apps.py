from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    """
    Leaderboard application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "leaderboard"

    def ready(self) -> None:
        import leaderboard.handlers  # pylint: disable=import-outside-toplevel, unused-import
